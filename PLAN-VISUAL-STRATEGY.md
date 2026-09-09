# Visual strategy: website, video, cards, products

**Written:** 2026-09-07 · **Author:** ux-frontend
**Direction it answers, verbatim from Phil:** *"a better visual strategy with the
website and products. Each should have terrific images and videos for all micro
zones."*

**Scope:** one document. Nothing else in the repository was changed. No git
command was run.

**Method:** every claim below was produced by opening the actual file, decoding
the actual video frame, or counting the actual corpus. Filenames and verdict
records were not trusted. Section 9 lists what I could not check.

---

## 0. The one-paragraph version

**The standard already exists inside this estate, and it was never propagated.**
Nine room pages carry figures drawn for the book, and two of them,
`ch31-image02` (an overhead entryway plan with five numbered zones and the line
*"one room, five small jobs"*) and `ch31-image07` (a shoe zone standard with
callouts, a traffic-flow arrow and a five-item standard panel), are as good as
anything in this category anywhere. Meanwhile the 107 zone heroes were made by
Stable Diffusion 1.5 at 768x576 and routinely do not depict their own subject: I
opened the approved shoe zone hero and it shows roughly eighteen pairs strewn
across a floor with no rack, under a caption reading *"An illustration of the
finished state."* So this is not a request to invent a look. It is a request to
**name the look we already achieved once, turn it into a test a machine can
apply, and run it across 114 zones, 20 rooms, 89 cards, 114 films and 159
products.**

Two things make that tractable today. Image **understanding** is not
billing-gated even though generation is, so the audit that produces the work
list is free and should run before a cent is spent. And the eleven room pages
with no photography are **not** sourceless: all eleven already have
`image-generation-prompts.md` written in the exact site palette, 71 prompts in
total, every one of those prompt sets including a zone plan. The brief I was
given said there was no source to import from. There are no finished images;
there is a complete written specification.

**Fixed same day, checked 9 September 2026 against the live code, not
re-asserted from the finding below.** This section originally reported 341 of
342 instruction slides across the 114 films cut off mid-sentence with a full
stop appended by the renderer, reproducing 24.5% of the authored method. That
was true when measured and was fixed in the same commit that introduced this
document (`2d99fecb`, 2026-09-07): `ops/video_zone.py`'s `beats()` now splits
every pass at sentence boundaries via `_sentence_chunks()` (never mid-clause)
and renders all six passes, not three. `ops/video_narrated.py`'s `build()`
calls `vz.beats()` directly, so the narrated pipeline inherits the same fix
with no separate change needed. Section 5.1 below is the original finding,
kept for the record; treat its present-tense claims as describing the state
before that commit, not the state of the code today. **Not verified: whether
the local rendered video files (not committed to git) have actually been
regenerated from the fixed code, and whether the 12 videos already live on
YouTube (uploaded by hand before this pipeline existed, per
`ops/youtube-published.json`) carry the fix: YouTube cannot replace an
uploaded file, so those 12 keep whatever was baked in at upload time
regardless of any later source fix.** No ffmpeg in this sandbox to re-render
and check either way.

---

## 1. What I opened, and what it showed

Twelve images, five video frames, three corpora, the production HTML set.

| Artefact | What I found by opening it |
|---|---|
| `build/heroes/zones/entryway--landing-zone.png` | A wooden tray on bare boards holding a wallet, a key, a pen and a keyring. Passes on subject. It is a catalogue still-life on an empty surface, with no wall, no door and no room: it shows the *object*, not the *zone*. |
| `build/heroes/zones/entryway--shoe-and-boot-zone.png` | ~18 pairs of boots and shoes loose on the floor. **No rack anywhere in frame.** The zone's own standard is *"Two pairs per person on the rack."* One boot is a yellow blob; another is a fur mass. This is the "before" published as the "after". |
| `build/heroes/zones/garage--hand-tool-wall-and-cabinets.png` | A pegboard densely hung with tools whose handles and heads are melted and anatomically impossible. **No painted silhouettes, no shadow board, no labels**: the entire organising idea of the zone is absent from the picture of it. |
| `build/heroes/zones/primary-bathroom--medicine-cabinet-or-wall-storage.png` | A sink floating off the wall with no visible support or plumbing; a cabinet with hinges rendered on both sides. Contents are toiletries; no medicine. Showroom styling, decorative vase of flowers. |
| `build/heroes/zones/kitchen--utensil-and-utility-drawers.png` | A wide shot of a run of **closed** drawers. The zone is the drawer interior. The subject is not merely wrong, it is structurally impossible to see. |
| `build/heroes/zones/patio-or-deck--grill-and-outdoor-cooking-zone.png` | A built-in stone outdoor kitchen with twin gas grills under a cedar pergola beside a lawn. Technically clean, aspirationally wrong: nothing here is a 30-minute quest, and it depicts a house most readers do not have. |
| `build/heroes/zones/family-room--board-game-and-puzzle-zone.png` (verdict `no`) | Correctly rejected. Reads as a bookshop wall, dozens of spines in garbled lettering. |
| `build/heroes/entryway/EM-003.png` (verdict `ok`) | A cabinet, a mirror, a handbag on hooks. **No keys, no bowl, no key hooks.** The card built on it prints six numbered callouts about keys. Confirmed by opening. |
| `build/cards-rendered/EM-003-front.png` | Pipeline B output. Genuinely clean: 750x1050, real Fraunces display, correct canon ("STRAIGHTEN"), family band, 30-second action, no garble possible. The only defect is the photograph inside the window. |
| `site/assets/cards/entryway/EM-005-...-front-md.jpg` | Live. Bottom third fully garbled: *"PHEE GUEST FRIENDLY aoaay"*, *"CARSENCE EARES"*, *"Rably nay be equipped"*, *"Ceobd Bnenony"*. |
| `site/assets/cards/entryway/EM-001-...-back-md.jpg` | Live. A large badge: **"7X LESS LIKELY TO BE TARGETED"**, unsourced, baked into pixels. |
| `site/assets/img/rooms/w/ch31-image02-840.jpg` | The best asset we own. Warm hand-drawn overhead plan, five zones outlined and numbered, icon medallions, dashed door-swing arc, *"one room, five small jobs."* Maps 1:1 onto our five entryway zone pages, **and is not clickable, because every label is a pixel.** |
| `site/assets/img/rooms/w/ch31-image07-840.jpg` | Shoe Zone Standard. Callout chips with leader lines, a TRAFFIC FLOW arrow, a five-item "THE STANDARD" panel with icons, a PRO TIP block. All type baked in, all of it legible and correct. |
| `site/assets/img/shine.jpg`, `site/assets/img/room-map.jpg` | Book figures 16-04 and 15-03, both excellent. Both used as generic decoration on shop tiles, **with the words "FIGURE 16-04" and "FIGURE 15-03" visible in the pixels**, on 22 and 4 product tiles respectively. |
| `build/cover.jpg` | Entirely typographic. Leads with the friction gauge, the device the book itself retired in favour of the before/after signature, in a red-amber-green ramp that is not the six-S palette. |
| Frames from `narrated-16x9/entryway--shoe-and-boot-zone-16x9.mp4` at 2 s and 40 s | 2 s: title card, bottom 45% empty. 40 s: **"...the trainers with the split sole all go, and."**, a sentence cut mid-clause with a fabricated full stop, burned into the pixels, spoken by the narrator, and repeated in the SRT. |
| Frame from `narrated-9x16/entryway--shoe-and-boot-zone.mp4` at 1 s | The same slide re-laid-out. Text occupies ~22% of a 1920 px-tall frame. As a Short this is dead on arrival. |
| Frame from `build/video/cards/EM-003-key-station.mp4` at 6 s | **The best moving frame in the estate.** Full-bleed art, karaoke captions with a terracotta highlight, real keys on real hooks, numbered pins. Two defects: a blurred letterbox top and bottom where a 4:3 source was padded into 9:16, and the caption *"The keys have no home"* over a picture in which every key is on a hook. |

### Three of these counts are not defects, checked 9 September 2026

The table below is accurate and reads like a defect list, which is a different
thing. Three of its rows were opened and turned out to be correct behaviour.
Recording that here because each one would otherwise be "fixed" by a later
cycle, and two of the three fixes would make the site worse.

**"Card faces in the gallery with `alt=""`: 144 of 144."** True, and correct.
Every card sits inside `<button class="flip" aria-label="Micro Zone card EM-001,
Front Door. Front is showing...">`, with the code and name also in visible text
beside it. The image is decoration behind a control that already names itself.
Giving those images alt text would make a screen reader announce each card
twice.

**"`<img>` tags site-wide missing `width`/`height`: 159 of 483, all on
shop.html."** True, and inert. `.product .ph` already carries
`aspect-ratio:4/3` with the image at `width:100%;height:100%;object-fit:cover`,
so the box is sized by CSS before the image loads and there is no layout shift
to prevent. Adding the attributes would change no layout and would declare a 3:2
intrinsic size on an image displayed at 4:3.

**"Rejected zones still carrying shipped derivatives: 3 zones x 9 files = 27
orphans."** Was true, is not any more. Checked every file in
`site/assets/zones/` against `ops/hero-verdicts.json`: zero belong to a rejected
zone, and zero are referenced by any page. Cleaned up since this plan was
written.

The rows that ARE real defects and remain so: 7 zone pages with no image, 11 of
20 room pages with none, 0 of 11 room chapters with finished images, and the
whole article surface below.

---

### The surface this plan did not have, added 9 September 2026

This plan counts zone heroes, room images, shop tiles, card faces, films and
book chapters. It contains the word "article" zero times, and there are 30 of
them.

| Measurement | Value | How |
|---|---|---|
| Article pages | **30** | `site/articles/*.html` |
| Article pages with content imagery | **0 of 30** | `<img>` and `<picture>` count per file |
| SVGs per article | **exactly 3, all chrome** | the logo twice and the mobile menu icon |
| Median article length | about **1,900 words** | tag strip and count |
| Articles written by a generator | **2 of 30** | only `ops/build_articles.py` writes to `site/articles/` |

The first measurement I took said "0 images" and was wrong in a way worth
recording: it counted `<img>` and `<picture>` and missed inline `<svg>`, so it
reported zero where there were three. Opening them showed all three are the
header logo, the footer logo and the menu button. The corrected finding is
narrower and still true: thirty articles of about 1,900 words each, on the
surface built for answer engines, with nothing to look at.

**No action taken, deliberately.** Twenty-eight of the thirty are hand-authored
files with no generator behind them, so illustrating them is twenty-eight hand
edits, and doing that at the current traffic would be decoration rather than
work. Several map cleanly to a zone whose hero is already reviewed and approved
(keys to the landing zone, mail to the mail zone, the medicine cabinet to its
own), which is the honest route when it is worth taking.

### Social cards, measured and fixed the same day

A shared link is the one image a page shows to somebody who has not visited it.

| Measurement | Before | After |
|---|---|---|
| Pages with no `og:image` | **7** | **3**, all by design |
| `deck-gallery.html` social tags | **0 og, 0 twitter** | full card, room-aware image |
| `kit.html` social tags | **0 og, 0 twitter** | full card |
| `kitchen-deck.html` | og block present, **no image**, `summary` | image added, `summary_large_image` |
| `og:image` pointing at a missing file | 0 | 0 |

Sharing the page that shows every card in the free deck produced a bare link
with no title, description or picture. The gallery's image now follows its room
rather than being hardcoded, because that generator writes one page per deck,
and falls back to a real site image when a room has no chapter art yet, which is
why the Mudroom gallery shows the generic one.

The three remaining are correct as they are: `404.html` and `thanks.html` are
not pages anybody shares, and `deck/entryway-print-and-play.html` is a print
sheet that preflight already treats as chrome-free by design.

---

### Counted, not sampled

| Measurement | Value | How |
|---|---|---|
| Zone hero masters | 114, all exactly **768x576** | PIL over `build/heroes/zones/` |
| Verdicts | **107 ok, 7 no** | `ops/hero-verdicts.json` |
| Rejected zones still carrying shipped derivatives | **3 zones x 9 files = 27 orphans** | `site/assets/zones/` vs verdicts |
| Rejected zones with a hand-written subject waiting | **7 of 7** | `ops/hero-subjects.json` |
| Room pages with zero images | **11 of 20** | `<img>` count per file in `site/rooms/` |
| Zone pages sitting behind a blank room page | **63 of 114** | zone counts in `content.json` |
| Zone page length and image count | **3,484 words, 1 image** (shoe zone) | tag strip + count |
| Zone pages carrying a video | **12 of 114** | `youtube-nocookie` embed count |
| Zone hero alt text | 107 unique strings, median **9 words**, **92** ending *", illustrated."* | regex over `site/zones/` |
| Room-page alt text (book figures) | **60 to 100 words**, naming every zone and every callout | same |
| Card faces in the gallery with `alt=""` | **144 of 144** | `site/deck-gallery.html` |
| Card faces within 2% of the 5:7 trading-card ratio | **15 of 144.** Median 1.350, range 1.000 to 1.658 | width/height attributes |
| `<img>` tags site-wide missing `width`/`height` | **159 of 483, all on `shop.html`** | regex over `site/**/*.html` |
| Distinct images serving 159 shop products | **11**, reused 10 to 22 times each | `src` frequency on `shop.html` |
| `<img>` tags in the Whole House Print Pack and the Standards Pack | **0 and 0** | grep |
| Passes authored per zone | **6 of 6, for all 114** | `content.json` |
| Passes rendered into each film | **3** | `ops/video_zone.py`, `shown >= 3` |
| Pass texts exceeding the renderer's 26-word cap | **680 of 684** (median 46 words, max 134) | corpus count |
| Instruction slides truncated across the 114 films | **341 of 342** | same |
| Films with at least one truncated instruction | **114 of 114** | same |
| Share of the authored method reaching the screen | **24.5%** (8,891 of 36,339 words) | same |
| Films silently dropping clauses from "what done looks like" | **87 of 114** | clause-split replay |
| Shoe zone 16:9 video bitrate | **162 kbps** at 1920x1080p30 | ffprobe |
| Room chapters 40-50 with finished images | **0 of 11** | Desktop chapter packages |
| Room chapters 40-50 with authored image prompts | **11 of 11, 71 prompts** | `image-generation-prompts.md` in each |

---

## 2. What "terrific" means, as a test

Adjectives are unfalsifiable. The card pipeline already has the right shape: the
callouts printed on a card are read out of the card's own record, and the
picture must contain them, so the test and the artefact cannot drift apart.
Below is that idea extended to a zone hero, a room image and a zone film, using
fields that **already exist in the repository for all 114 zones**.

### 2.1 The zone hero test

Source of truth: `done_looks_like` in `content/manual/source/content.json`,
authored for all 114 in countable terms, plus `diagnosis.frictions[].symptom`
where it exists (12 zones today, the rest gated behind the pilot read).

| # | Item | Kind | Verified failure in today's set |
|---|---|---|---|
| **Z1** | The zone's **primary noun is visible and is the largest object in frame**. | **HARD** | `EM-003`: no keys. `kitchen--utensil-and-utility-drawers`: no drawer interior. |
| **Z2** | Every **countable clause** in `done_looks_like` is checkable by counting in the picture. *"Two pairs per person on the rack"* requires a rack, and requires the count to hold. | **HARD** | `entryway--shoe-and-boot-zone`: no rack, ~18 pairs. |
| **Z3** | The picture depicts **no symptom** the zone's own `diagnosis` names as the problem. The negative image of the standard. | **HARD** | `garage--hand-tool-wall-and-cabinets`: no marked home for any tool, which is the zone's own stated root cause. |
| **Z4** | The **zone occupies at least 40% of frame area**. Not a room shot with the zone somewhere in it. | soft | `kitchen--utensil-and-utility-drawers`: 0%. `laundry-room--detergent-and-treatment-zone`: the detergent shelf is under 10%. |
| **Z5** | If the zone is an **interior** (drawer, cabinet, closet, fridge, under-sink, medicine cabinet), the container is **open and its contents legible**. | **HARD** | `kitchen--utensil-and-utility-drawers`: closed. |
| **Z6** | **Zero readable or pseudo-readable lettering**, zero brand marks, zero QR-like blocks, zero human faces. | **HARD** | `family-room--board-game-and-puzzle-zone`: garbled spines throughout. |
| **Z7** | **Everything is physically possible.** Objects have support. Hinges are on one side. Handles, legs and limbs are the right count and shape. | **HARD** | `primary-bathroom--medicine-cabinet`: levitating sink, hinges both sides. `garage--hand-tool-wall`: melted tools. |
| **Z8** | **An ordinary home, not a showroom and not a listing photograph.** Operational test: *could the state shown be reached, in this room, in the session length the page claims, without buying furniture?* | soft | `patio-or-deck--grill-and-outdoor-cooking-zone`: a built-in stone outdoor kitchen is not a 30-minute quest. |
| **Z9** | **Two composed frames per zone**: 3:2 for page and card, 9:16 composed for video and Pinterest. Never a crop, never a pad. | production | 0 of 114 today. The card film shows exactly the blurred letterbox this prevents. |
| **Z10** | **Master at least 2048 px on the long edge**, sRGB, retained and never overwritten. | production | 114 of 114 are 768 px. `MEDIA-OPERATIONS-PLAN.md` §3.1 asks for 3000. |

**Passing:** no HARD failure, and at least 8 of 10 items satisfied.

**Procedure:** two vision runs with the item order shuffled must agree;
disagreement escalates to a person. The verdict record stores the sha, the
checklist it was judged against **and the answer to every item**, so *"EM-003
passed review"* becomes a statement somebody can falsify. Today
`hero-verdicts.json` stores one word.

**Why the old review could not catch any of this.** `ops/review_heroes.py`
builds contact sheets twelve to a page at 320 px wide. At that size the only
question a reviewer can actually answer is *"is this an entryway?"*, and the
keyless key station answers it yes. The verdict was not dishonest; it was a
correct answer to a question too weak to matter, asked at a resolution that
could not support a better one.

**The root cause is already written down in this repository, in
`ops/hero-subjects.json`'s own `_comment`:** the zones that failed are the ones
whose names are *a rule or a place rather than a thing*, "floor and circulation
path", "paper and household backstock", "surface rail and safety zone", *"there
is nothing in those sentences for a model to draw, so it renders the room and
ignores the zone."* The corrective pattern is written there for all seven
rejects and it is the right one: `close up of six board game boxes stacked flat
on a wooden shelf`. Concrete, countable, under twenty words. **That pattern
should be applied to all 114 subjects, not only the seven that failed loudly**,
and doing so costs nothing.

### 2.2 The room image test

A room page answers a different question: **"what can I improve here?"** No
photograph of a tidy room answers it. `ch31-image02` does. So the room image is
not a hero. It is **a zone map plus a signature pair**.

**Zone map**

| # | Item | Kind |
|---|---|---|
| **R1** | The map shows **exactly as many numbered zones as the room has zone pages**. Machine-checkable against `content.json`: Entryway 5 = 5, Garage 7 = 7. | **HARD** |
| **R2** | **Every label is live text set in SVG over a textless base**, selectable, translatable, keyboard reachable, **and each label links to that zone page**. | **HARD** |
| **R3** | The numbering is the **order the room should be worked**, not arbitrary. Walls before floor; bench before slab. | soft |
| **R4** | The view is a **plan or axonometric of the archetype**, not a specific house, so a reader can find their own room in it. | soft |
| **R5** | **No baked text of any kind** outside the SVG layer. | **HARD** |
| **R6** | Alt text **names every zone and the relationships between them**. The standard already exists in the repository: `ch31-image02`'s alt is 92 words and names all five zones and the door swing. | **HARD** |

**Today 0 of 20 rooms pass R2 and R5**, including the nine that have pictures,
because even the excellent entryway map has its labels baked as pixels and none
of its five zones is clickable. This is the single largest quality,
accessibility, internationalisation and internal-linking win available anywhere
in the estate, **and the overlay component that fixes it needs no billing at
all.** It also makes the map maintainable: when a zone is renamed, the label
changes and the picture does not have to be regenerated.

**Signature pair (before and after)**

| # | Item | Kind |
|---|---|---|
| **S1** | Same room, same camera position, same light, same furniture. **Only the state changes.** | **HARD** |
| **S2** | The after is **reachable in the time the page claims**. New cabinetry is a fail. | **HARD** |
| **S3** | The before is **ordinary, not squalid.** We do not make a normal household problem look like a moral failure. | **HARD** |
| **S4** | "before" and "after" are set in the SVG layer, not in the pixels. | soft |
| **S5** | The caption says it is an illustration. | **HARD** |

### 2.3 The zone video test

| # | Item | Kind |
|---|---|---|
| **V1** | **Every sentence on screen is a complete sentence from the corpus.** No word-count truncation, ever. If a pass is 46 words it takes two slides. | **HARD** |
| **V2** | All **six** passes appear in the long-form cut. A film showing Sort, Straighten and Shine is teaching 3S. | **HARD** |
| **V3** | The picture on screen and the line spoken over it **do not contradict each other**. Z1-Z3 applied to the pairing, not just the frame. | **HARD** |
| **V4** | The vertical cut opens on the **standard**, the one sentence saying what the viewer will have at the end, inside the first 2 seconds. | soft |
| **V5** | 9:16 frames are **composed**, never padded, never auto-cropped. | **HARD** |
| **V6** | Loudness within 0.5 LU of **-14.0 LUFS**, true peak below -1.0 dBTP. | soft |
| **V7** | Video bitrate **8-12 Mbps at 1080p** in any render containing a photograph. | soft |
| **V8** | Caption cues cut at **narration phrase boundaries**, not slide boundaries. | soft |
| **V9** | The description link **resolves to a 200 on our own domain**. | **HARD** |

**As measured before the 2026-09-07 fix (`2d99fecb`, see the note at the top
of §1): all 114 films failed V1 and V2. Both are fixed in the code today; see
that note for what is and is not verified about the rendered/published
files.** 7 of the 12 published films fail V9 and remain unfixed; see A6 in
`PLAN-MEDIA-2026-09-07.md` (blocked on egress to read the live YouTube
descriptions or on Phil pasting them).

---

## 3. One visual system

### 3.1 There are currently five, and I can name them by file

1. **The declared system.** `site/assets/css/site.css`, `ops/video_zone.py` and
   `ops/card_spec.py` agree exactly: paper `#F7F2E9`, ink `#2B2622`, terracotta
   `#BC4B2A`, honey `#DDA63A`, green `#4E7A57`, spark `#CB4B36`, slate
   `#3C5A6B`, sustain `#6E5B8B`, deep `#22323C`, rule `#E2D8C4`; Fraunces
   display, Inter interface, Newsreader italic. **This is the system. It is
   already consistent across three subsystems and it should not change.**
2. **The book figures.** Warm paper, forest-green accent, a transitional serif
   that is not Fraunces, white callout chips with 1 px leader lines and dot
   terminators, a "FIGURE nn-nn" tab. Our best work, and off-palette.
3. **The SD 1.5 zone heroes.** Photoreal renders, 768x576, no callout grammar,
   frequently the wrong subject.
4. **The shipped card faces.** Sketch illustration, dark green, every word baked
   in, 144 different aspect ratios.
5. **The book cover.** A red-amber-green gauge ramp appearing nowhere else,
   attached to a device the book retired.

A person who watches a Short, lands on the zone page and then opens the deck
gallery currently sees three different products.

### 3.2 What is shared, without exception

- **The palette.** Those ten tokens and nothing else. **The six-S hues are
  semantic, never decorative:** terracotta only ever means Sort, honey only ever
  means Straighten, and so on, on the page, in the film's progress spine, on
  the card's family band, in the print pack. No eleventh colour is invented for
  a new surface; `card_spec.py` already sets the precedent by taking two
  documented deep shades rather than inventing hues for its seventh and eighth
  families, and by pairing every colour with a glyph so meaning never rests on
  colour alone.
- **The type.** Fraunces 600 display, Inter 600/700 interface, Newsreader italic
  for the standard and the quoted voice. Self-hosted woff2 already in the
  repository and already loaded by the same headless browser that renders the
  slides and the cards, so print, web and video are set in the same metal.
- **The six-S spine.** The six-segment progress bar is the strongest recognition
  device we own, it already appears in the film and on the thumbnail, and it
  costs nothing to add to the zone page, the card back and the room map. Give
  completed segments a tick or a fill fraction so the meaning is not colour
  alone.
- **The callout grammar.** White chip, 1 px leader line, dot terminator,
  uppercase label above a sentence. Lifted exactly from `ch31-image07` and
  `shine.jpg`, which prove it works. **Set as SVG over a textless base, never
  drawn into the picture.**
- **The circled numeral.** One face, one size ramp, on maps, on cards, on
  callouts, matching the numbers in the corresponding list of steps.
- **Radius.** 14 / 22 px on the web, 37 px (0.123 in) on a card, per
  `card_spec.py`.
- **The honest caption.** Every generated picture is captioned as an
  illustration. This is a constraint, not a problem to design around, and it is
  also a **design advantage**: an illustration is allowed to show a dashed door
  swing, a numbered zone, a cutaway drawer and a traffic-flow arrow. A
  photograph is not.

### 3.3 What is deliberately different

| Surface | Difference | Why |
|---|---|---|
| Card art vs zone hero | Cards may be looser, warmer illustration; the site leans towards render. | A card is held at 60 cm and read in three seconds; a page hero is scanned at arm's length beside 3,500 words. Both textless, both same palette. |
| Film ground | Dark `#22323C` for the hook and the closing call; paper for the work. | It is the only reason the film reads as chaptered rather than as one long slide. Keep it. |
| Vertical vs horizontal | Vertical is a **hook** under 45 s: standard, one pass, one victory condition. Horizontal is a **document** of 4 to 6 minutes: all six passes, chaptered, sidecar SRT. | Two formats serving two jobs beats one format serving neither. |
| Book vs website | The book keeps "FIGURE nn-nn" tabs. The website must never show one. | A shop tile reading "FIGURE 16-04" tells a buyer they are looking at a page torn out of something else. It is on 22 tiles today. |
| Print vs web | 300 dpi CMYK-safe derivatives from the same master; AVIF, WebP and JPEG on the web. | Already specified in `MEDIA-OPERATIONS-PLAN.md` §5 and already built. |

---

## 4. The 114 zones: what each needs, in what order

Ordering rule, from `GOALS.md`: the constraint is arrivals, and distribution
beats production. So order by *can a stranger see it today*, then *is it free*,
then *does skipping it cause paid work to be redone*.

### Wave 0: free. No billing, no OAuth. Do all of it first.

| # | Work | Why it is first |
|---|---|---|
| **0.1** | **Run the §2 accept tests over all 346 existing images** (114 zone heroes, 88 card heroes, 144 card faces), storing per-item answers rather than a verdict word. | Image understanding is not gated. This is the only thing that converts *"re-shoot 107"* into a list, and it is the difference between spending $47 and spending $15. |
| **0.2** | **Withdraw every hero that fails a HARD item** until it is replaced. | Text-only is honest; a picture contradicting its own caption is not. The precedent is already set and already correct: 7 zones ship text-only today. |
| **0.3** | **Delete the 27 orphan derivatives** for the three rejected zones. | They ship inside the Docker image. If one is ever wired by mistake, it publishes a rejected image. |
| **0.4** | **Replace the 107 templated hero alts** with real descriptions. The vision run in 0.1 returns a literal description of each image for free. | *"The Shoes and Boots in the Entryway, illustrated."* is nine words describing nothing. The room pages already show the standard at 60 to 100 words. |
| **0.5** | **Give the 144 card faces alt text.** | The product gallery is invisible to a screen reader and carries zero image SEO, on a site whose measured constraint is arrivals. |
| **0.6** | **Put `width`/`height` on the 159 images on `shop.html`.** | Layout shift on the one page with commercial intent. All 159 are on that page. |
| **0.7** | **Rewrite all 114 hero subjects to the `hero-subjects.json` pattern**: concrete, countable, under twenty words, naming objects rather than the zone's name. | The single largest determinant of whether the paid batch produces usable output, and it costs nothing. |
| **0.8** | **Build the SVG zone-map overlay component** and retrofit the entryway map to live, linked labels. | R2/R5. Not blocked, needed by all 20 rooms, and it turns the best image we own into navigation. |
| **0.9** | **Move the frozen style source into the repository.** `ops/generate_card_art.py` reads it from a Desktop path outside version control. | This is the one thing that can silently turn an overnight batch into a second visual identity, and the drift would only be detectable after the money is spent. |

### Wave 1: first money. The pictures a stranger can already reach.

**1.1 The 7 rejected zone heroes.** `family-room--board-game-and-puzzle-zone`,
`home-office--file-storage`, `home-office--printer-and-scanning-station`,
`mudroom--family-hook-zone`, `nursery--crib-and-sleep-zone`,
`primary-bathroom--under-sink-cabinet`, `workshop--material-rack`. All seven
already carry hand-written concrete subjects (verified). Seven live pages
completed for the price of fourteen images.

**1.2 The heroes that failed a HARD item.** Four are already named by opening
them: the shoe zone (Z2, Z3), the garage tool wall (Z3, Z7), the medicine
cabinet (Z7), the kitchen utensil drawers (Z1, Z4, Z5). Wave 0.1 sizes the rest.

**1.3 The 89 Entryway card heroes, textless.** First among the paid work for
four compounding reasons: the deck is the flagship and its picture is on
`shop.html`; seventeen cards are withheld from the box today purely because of
defects baked into pixels, so a buyer receives an incomplete deck whose own
contents card indexes more zones than the box holds; the receiving pipeline is
finished and proven, with 178 cards already rendering correctly; and it is the
smallest job on the list. Once these exist, **every remaining text defect in the
deck becomes a JSON edit costing nothing.**

### Wave 2: the 11 blank room pages. 63 zone pages sit behind them.

Garage 7 zones, Primary Bathroom 7, Nursery 6, Laundry 6, Home Office 6,
Workshop 6, Mudroom 6, Patio or Deck 6, Guest Bathroom 5, Hall Closet 5, Stair
Landing 3.

**These are not sourceless.** Every one has `image-generation-prompts.md` in its
Desktop chapter package, written in the house style and citing the palette hexes
directly. Chapter 45's opens: *"warm paper background, editorial illustration,
serif display type, muted terracotta, honey, slate, and green accents. No logos,
no brand names, no readable packaging or label text, no QR codes."* Chapter 40's
adds *"paper #F7F2E9 ground, ink #2B2622 line ... No real infant depicted;
suggest scale, not a face."* 71 prompts across the eleven rooms, every set
including a zone plan and a before/after signature pair. Move them into the
repository (Wave 0.9) before generating.

Order within the wave: **Garage, Home Office, Laundry, Primary Bathroom,
Mudroom** first, most zone pages behind them, and the room names people
actually search.

Each room needs **three** images, not one: the textless map base, and the two
frames of the signature pair. The remaining four prompts per room are optional.

### Wave 3: the remainder of the 107, two compositions each.

Deliberately last and deliberately partial: re-shoot what failed a soft item and
what a full-bleed film will magnify, not all 107 by default. The audit decides,
not a schedule.

### Wave 4: costs nothing extra.

114 thumbnails and 114 films rebuilt from the same masters. No new generation at
all: the same picture serves the page, the card, the vertical film and the
thumbnail.

---

## 5. Video: what changes now that the page is 3,500 words

**The code quoted in §5.1 below is the pre-fix version, kept as the record of
what was found. `ops/video_zone.py` no longer contains either snippet as of
`2d99fecb`, 2026-09-07; see the note at the top of §1.**

### 5.1 The honest answer to the question asked

The question was whether slide-and-narration is still right now that zone pages
carry all six passes in depth. **The format is not the first problem. The film
misquotes the page.**

`ops/video_zone.py` does two things that a deep page makes indefensible:

```python
if len(text.split()) > 26:
    text = " ".join(text.split()[:26]) + "."
```

and

```python
if not text or shown >= 3:
    continue
```

The first cuts an instruction at 26 words and **appends a full stop**, producing
a sentence that looks complete and is not. Across the corpus, 680 of 684 pass
texts exceed 26 words (median 46, max 134), so **341 of the 342 instruction
slides in the 114 films are truncated**, in the burned pixels, in the spoken
narration and in the SRT. The one I pulled off disk reads *"Odd shoes, outgrown
children's pairs and the trainers with the split sole all go, and."* The source
sentence ends *"...and so does the tin of polish that has dried solid."* A
separate clause-splitting bug drops content from *"what done looks like"* in 87
of 114 films; the shoe zone's caption 7 reads *"A clear stretch of floor a full
stride wide between the door"* and the source says *"between the door and the
rack."*

The second stops after three passes. Every zone has six authored. **Safety
appears in zero of the 114 films.** For a household product with ladders,
solvents and toddlers in it, that is the wrong three to drop.

Together: **24.5% of the authored method reaches the screen**, and most of what
does is a false sentence.

**So: fix the quotation before changing the medium.** A photo-led, full-bleed
redesign built on the same corpus would put a fabricated sentence in 100 pt type
across a photograph. That is the definition of work that has to be redone. Note
also that this is a *different* defect from the 412 truncated YouTube
descriptions already logged in `PLAN-MEDIA-2026-09-07.md` A7: that one is in
`ops/build_youtube_metadata.py` and can be fixed by editing text. This one is
baked into pixels and audio and needs a re-render. There are two independent
truncators in this pipeline.

### 5.2 The next version, in order

1. **Never truncate.** ~~Split on sentence boundaries and add a slide.~~ **Done,
   `2d99fecb`, 2026-09-07** (`_sentence_chunks()` in `ops/video_zone.py`). The
   film gets longer, which is correct: the page is 3,484 words and the film is
   126 seconds.
2. **All six passes** in the long-form cut. **Done, same commit** (`order` in
   `beats()` now renders sort/straighten/shine/safety/standardize/sustain).
3. **Two cuts, two jobs.** Vertical ≤45 s: the standard as the hook in the first
   two seconds, one pass, one victory condition, full-bleed picture, karaoke
   captions in the terracotta highlight the card prototype already uses.
   Horizontal 4 to 6 minutes: all six passes, chapter markers on the six-S
   spine, sidecar SRT.
4. **Put the picture in, but only where the hero passes §2.1.** That is an
   honest subset, it is free, and it produces the first real evidence about the
   format before a cent is spent. `ops/video_zone_photo.py` already exists.
5. **Composed 9:16 heroes.** The card prototype shows the blurred letterbox
   exactly as predicted. Padding 4:3 into 9:16 is the same mistake as
   auto-cropping 16:9, wearing a different hat.
6. **Bitrate to 8-12 Mbps, in the same render that adds pictures, not before.**
   Measured today: 162 kbps at 1080p30. Invisible on flat cream; blocking and
   mush on a photograph.
7. **-14 LUFS.** Measured -15.0 to -15.2. YouTube normalises down and never up,
   so every film plays about a decibel quieter than everything around it.
8. **Caption cues at narration phrase boundaries.** Cue 1 of the shoe zone
   currently merges the room name, the zone name and half the opening sentence,
   then splits the rest across cue 2.
9. **The orphaned keyword chip**, in all 114, both orientations.
10. **The description link.** 7 of the 12 published films send every clicking
    viewer to a 404. Thirteen `return 301` blocks in `site/nginx/default.conf`
    fix it without touching OAuth, using a pattern that file already uses on
    lines 187-188. **No aspect of video quality matters more than this**,
    because the link is the only path from a view to the site and arrivals are
    the constraint.

**Thumbnails follow the same expired premise.** `ops/build_thumbnails.py` states
as a design rule *"Real contrast, no photograph behind the type. There is no
per-zone photography."* True when written, false now. At the 168 px a thumbnail
is actually seen, a cream card with black type loses to a real before-and-after
every time, and thumbnail click-through is the largest single lever on the whole
video stream. Fold it into Wave 4 at no extra generation cost.

**What I would not change: the narration.** The neural voice is consistent,
loudness is consistent to within 0.2 LU across a ten-file sample, and the script
comes from the same corpus as the page. It is the healthiest part of the
pipeline.

---

## 6. Products

### 6.1 The card decks

**Retire pipeline A. Ship pipeline B. Spend money only on textless
photographs.**

The measurement that settles it: **only 15 of 144 shipped card faces are within
2% of the 5:7 trading-card ratio.** The median is 1.350 and the range runs 1.000
to 1.658, because they were sliced out of generated sheets rather than composed
on a canvas. A deck whose cards are not the same shape is not a deck.
`ops/render_cards.py` produces 750x1050 exactly, behind a 7 pt minimum-type gate
and an overflow gate, and 178 of them already exist and are correct.

Everything else follows from the same change. The garbled bands on EM-005 and
EM-006, `HŒUSE` on EM-002, the ghost word "FRONT" on EM-007 and EM-012, the 7X
badge on EM-001, and every dangling card code all become **JSON edits costing
nothing**, because the words stop being pixels.

Two things must happen before the good pipeline renders, or it makes the trust
position worse rather than better:

- **The 27 unsourced numeric claims still in `build/cardtext/`**, 17 of them on
  cards shipped today. Blurry pixels on a low-traffic gallery become crisp 12 pt
  type on a product we sell. `CLAUDE.md` §8 forbids fabricated statistics
  outright.
- **The nine cards with a recorded verdict of `no` that ship anyway.** The zone
  pipeline gates on verdict value; `ops/split_deck_cards.py` never reads one.
  One of the two paths is right.

**Kitchen deck:** `card_spec.FAMILY` holds only the Entryway families, so 65 of
72 Kitchen cards would print as identical dark cards. Half a day, and it must
precede any Kitchen render.

### 6.2 The print packs

`build/6S-Whole-House-Print-Pack.html` and `build/6S-Standards-Pack.html`
contain **zero `<img>` tags between them.** A Standards Pack whose entire job is
to show what good looks like has no pictures in it.

This is the cheapest product visual win available and almost none of it needs
generation. **The standard for a print pack is one zone map per room and one
callout diagram per standard, both SVG**, drawn from `content.json`: printable
at any size without loss, translatable, revisable when a zone is renamed without
regenerating a picture, and weightless. The same overlay component built in Wave
0.8 serves the website and the print packs from one source.

### 6.3 The book

- **The cover** is entirely typographic and leads with the friction gauge, the
  device the book itself retired in favour of the before/after signature, in a
  red-amber-green ramp that is not the six-S palette. It is the only 6S Success
  artefact whose colours carry no meaning. It should lead with the signature
  pair or a zone map. Both already exist and both are the best images we own.
- **Chapters 40-50 have zero images** while 31-39 carry three to seven each.
  That gap is inherited exactly by the website, which is why eleven room pages
  are blank. **Fixing the eleven room pages and fixing the book's second half is
  the same 71 prompts.** One programme, two products, one bill.

### 6.4 The shop

159 products share **11 images**, reused 10 to 22 times, and three of the eleven
carry a book figure number in the pixels. Doing this properly is 159 images and
a week, against a shop with one lifetime customer, so it is not a Wave 1 job.
The proportionate move is **one distinctive image per product family**, deck,
mini deck, print pack, standards pack, kit, book, consulting, corporate, which
is roughly eleven images, plus cropping the figure-number tabs out of the three
that leak them, which is free.

---

## 7. Cost and sequence

Prices are the ones recorded in `ops/generate_card_art.py` for
`gemini-3.1-flash-image`: **$0.045 at 0.5K, $0.101 at 2K**, noted there as
fetched 2026-09-04. **I did not re-fetch them; treat them as three days old.**
Retry multiplier 1.4x, which is what the accept test buys: you pay for a second
candidate only when the first failed a test, instead of always paying for three
and picking by eye.

### Free today, and about a week of one operator

Everything in Wave 0; the full re-render (CPU only, the truncation and
six-pass fixes themselves already shipped, `2d99fecb`); the Kitchen family
taxonomy; the SVG overlay component and the
entryway retrofit; the print-pack diagrams; -14 LUFS, the chip fix and the
caption cue boundaries; the 13 nginx redirects; the card corpus claim rewrite;
moving the style source into version control. **None of it waits on anyone, and
every item on it is something that, if skipped, causes generated images to be
redone.**

### Behind the billing click

| Wave | Finals | Requests (1.4x) | At 2K | At 0.5K |
|---|---|---|---|---|
| 1.1 · 7 rejects x 2 compositions | 14 | 20 | $2.02 | $0.90 |
| 1.3 · 89 card heroes, textless | 89 | 125 | $12.63 | $5.63 |
| 1.2 · hard-fail re-shoots, **estimated ~50 x 2** | ~100 | 140 | ~$14.14 | ~$6.30 |
| 2 · 11 rooms x (1 map base + 2 signature frames) | 33 | 46 | $4.65 | $2.07 |
| 3 · soft-fail re-shoots, remainder x 2 | ~100 | 140 | ~$14.14 | ~$6.30 |
| 4 · thumbnails and films | 0 | 0 | $0 | $0 |
| **Programme total** | **~336** | **~471** | **~$47.6** | **~$21.2** |

Waves 1.1 and 1.3 together are **$14.65 at 2K** and they finish the flagship
product: the fabricated statistics leave the deck permanently, the 17 withheld
cards are released, and the deck's own contents card becomes true.

**The 1.2 and 3 rows are estimates, not measurements.** They rest on a sample of
eight heroes, four of which failed a hard item. Wave 0.1 replaces both with a
count, and it is free.

At the fixed three-candidates-per-image the media plan currently specifies, the
same programme is about 1,008 requests and $101 at 2K. **None of these is a
monthly run rate.** They are one-time programme costs, and the accept test means
an image is paid for once.

Escalation policy: flash for candidates; escalate an individual image to
`gemini-3-pro-image` only after it has failed the accept test three times on
flash.

### The critical path

```
0.7 rewrite 114 subjects ──┐
0.8 SVG overlay component ─┼─► 0.1 run the accept test over all 346, free
0.9 style src into repo ───┘                   │
                                               ▼
                     the list of what genuinely needs regenerating
                                               │
                     ┌─────────  BILLING CLICK  ─────────┐
                     ▼                                   ▼
        wave 1: 7 rejects + 89 card heroes      wave 2: 11 room bases
                     │                                   │
                     ▼                                   ▼
          render pipeline B, retire A          map labels as live SVG links
                     │                                   │
                     └──────────► wave 3 ◄───────────────┘
                                     │
                                     ▼
              rebuild 114 films + 114 thumbnails, no new generation
```

**The click is nearly last on the critical path, not first.**

---

## 8. What I would not do

- **I would not generate a single image before the audit runs.** It is free, and
  it is the only thing that turns "re-shoot 107" into a list. Skipping it means
  paying to replace images that were fine while keeping ones that are not, with
  no mechanism to stop a new keyless key station passing again.
- **I would not photograph real homes, commission photography, or let any
  caption imply a render is a photograph.** The honest caption stays. It is also
  a design advantage: an illustration is allowed to draw a dashed door swing, a
  numbered zone and a cutaway drawer.
- **I would not buy stock photography.** It would be a sixth identity and it
  cannot depict a specific micro-zone standard, which is the entire product.
- **I would not commission art for a second deck.** `ROADMAP-2026-2029.md` §4
  already says deck 2 waits for evidence deck 1 is wanted, and this document
  does not reopen a settled decision.
- **I would not redesign the film format before fixing the truncation.** It
  would produce prettier false sentences.
- **I would not chase a 4K master.** The media plan's 3840x2160 line is
  aspirational; we render 1080p and the measured defect is 162 kbps, not
  resolution. Either hit 1080p properly or correct the plan to say so.
- **I would not add motion graphics, transition packs, a music bed or a
  mascot.** None of them helps a person standing in a room holding a phone.
- **I would not A/B test any of this.** The experiment registry computes 1,427
  days to significance at current traffic.
- **I would not build 159 bespoke product images** for a shop with one lifetime
  customer. Eleven family images, then stop.
- **I would not retrofit the nine existing book-figure room pages' baked labels
  before the eleven blank rooms have anything.** A worse-but-present picture
  beats a better-but-absent one.
- **I would not re-record the narration.**
- **I would not use the six-S hues decoratively anywhere**, on any surface, for
  any reason. The moment terracotta means "nice warm accent" as well as "Sort",
  the strongest recognition device we own stops working.

### What cannot move until traffic exists

Stated plainly, because pretending otherwise is how this repository has produced
work below the constraint before.

- **Which thumbnail style wins.** 12 published videos and 2.0 visitors a day is
  no click-through signal at all. Everything in this document is judged against
  a written standard, not against performance, and that is the honest position
  until there is a denominator.
- **Whether photo-led verticals beat typographic ones.** Wave 0's free subset
  produces the first evidence, and even that will be thin.
- **Whether card art should be illustration or render.** I have an opinion,
  illustration, because it composes reliably at our budget and it is honest
  about being a diagram, and no evidence.
- **Per-SKU product photography, and any image spend justified by conversion.**
  The conversion denominator is one customer.
- **Pinterest and Instagram crop programmes beyond generating the files.** The
  accounts do not exist, and creating them is Phil's, not an operator's.

---

## 9. What I did not check

Per `CLAUDE.md` §0.4, stated as loudly as what I did.

- **I opened 12 of 346 images and 5 video frames.** The failures named in §1 are
  confirmed by opening those files. They are not a measured failure *rate*. Wave
  0.1 produces the rate; the four-of-eight hard-failure sample is the basis of
  the §7 estimates and should be treated as a guess until replaced by a count.
- **I did not re-test whether image generation still returns HTTP 429.** The
  429-with-`limit: 0` finding comes from `PLAN-MEDIA-2026-09-07.md`, dated today
  but measured by another operator. I did not send a request.
- **I did not re-fetch Google's image prices.** They come from
  `ops/generate_card_art.py`, recorded there as fetched 2026-09-04.
- **I verified nothing against the live domain.** Every measurement here is
  against the repository and the Desktop video folder. The 7X badge being
  byte-identical in production is an inherited finding, not one I reproduced. So
  is the count of nine shipped cards carrying a `no` verdict, and so are the 412
  truncated YouTube descriptions.
- **I did not open all 114 films.** Format statistics come from ffprobe on one
  16:9 and one 9:16 file, plus the corpus replay that produced the 341-of-342
  count. The truncation itself I confirmed three ways: in the decoded video
  frame, in the SRT, and in the renderer source read against `content.json`.
- **I did not check the 144 card faces for the QR-imitating block.** The review
  that reported it was written against an older 35-image set, and the 12 faces I
  opened do not contain one. Absent from twelve is not absent from 144.
- **I did not test the vision model's error rate.** The §2 tests are designed
  around a known permissiveness failure, it answers `true` to category words
  such as "medicine" for a cabinet holding only toiletries, which is why every
  item is a discriminating noun and why two shuffled runs must agree. That is a
  design response to one observed failure, not a characterised error rate.
- **I did not verify that the 71 Desktop prompt files are complete or
  self-consistent.** I opened four of the eleven and counted headings in all
  eleven. Chapters 40, 41 and 42 use a different heading convention from 43-50,
  which is exactly the kind of difference that makes a naive counter report zero.
