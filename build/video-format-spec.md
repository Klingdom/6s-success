# 6S Success Video Format Spec v1

Owner: content-editor. Status: build-ready. Date: 2026-08-29.

Written against verified capability on this machine: ffmpeg 8.1.1 full (zoompan,
xfade, overlay, gblur, drawtext, ass, concat), PIL / numpy / OpenCV, headless
Edge/Chromium HTML-to-PNG at exact dimensions, Windows SAPI (David, Zira). No
stock footage, no music library, no AI video, no voice cloning. Nothing below
depends on anything outside that list.

---

## 0. Verified asset inventory (this constraint shapes everything)

| Asset | Count | Location / note |
|---|---|---|
| Card fronts, rendered | 90 | `site/assets/cards/entryway/*-front-lg.webp`, 760x1055 |
| Card backs, rendered | 90 | 760x996 |
| Card copy, structured | 90 | `build/cardtext/batch-0*.json`, `build/entryway-cards.json` |
| Room illustrations | 41 | `site/assets/img/rooms/ch31..ch39-*.jpg`, 1402x1122 or 1536x1024 |
| — before/after diptychs | 11 | classified from `ops/room-images.json` alt text |
| — zone maps / kit overheads | 9 | |
| — standard / procedure boards | 21 | |
| Generated heroes | 5 | `build/heroes/entryway/`, 1448x1086 |
| Site photographs | 13 | `site/assets/img/*.jpg`, 1535x1024 |
| Zone content, structured | 114 | `content/manual/source/content.json` — purpose, done_looks_like, six passes, the_call, watch_for, standard, trigger, shine_detail |

**The decisive fact: 109 of 114 micro zones have no image of any kind, and 11 of
20 rooms have no image of any kind.** The main format must therefore be fully
legible and fully branded with zero photography. Imagery is an optional opening
module, never a dependency. No format in this spec requires an image we do not
already have on disk.

---

## 1. Formats

Four formats. One rendering engine, one caption system, one type scale. They
differ only in beat map and source imagery.

| # | Format | Ratio | Duration | Applies to | Count |
|---|---|---|---|---|---|
| A | **Zone Reset** | 9:16, 1080x1920 | 24s | 114 micro zone pages | 114 |
| B | **Room Tour** | 9:16, 1080x1920 | 16s | 20 room pages | 20 |
| C | **Card Draw** | 9:16, 1080x1920 | 18s | 90 Home Quest cards | 90 |
| D | **The Answer** | 9:16, 1080x1920 | 20s | 22 articles + 15 core pages | 37 |

Total 261. The remaining budget is held for re-cuts of the top performers, not
spent on a fifth format.

**No 16:9 build in v1.** The page embed uses the 9:16 master in a 400px column;
YouTube takes it as a Short. A second aspect doubles 264 renders to buy a surface
with no audience yet. Revisit when one video clears 10k views.

---

## 2. Format A — Zone Reset, second by second

Canvas 1080x1920, 30fps, 720 frames. Coordinates are absolute pixels. Example
copy is the real Landing Spot record from `content.json`.

**Grounds.** Deep `#22323C` for hook, standard and trigger. Cream `#F7F2E9` for
the working middle. Ground changes are **hard cuts on a frame boundary**. There
are no fades anywhere in this format.

### 0.00–0.90 HOOK (deep ground)
- Frame 0 is fully composed and legible. Never fade up from black. Frame 0 is the
  thumbnail and the scroll-stopper.
- x 84, y 240: the friction gauge SVG from the homepage, 260px wide. Needle
  sweeps `-58deg → 0deg` over frames 0–22, easing `cubic-bezier(.6,.02,.2,1)`.
  Only moving element in the beat.
- x 84, y 620–1020, width 820: the hook line. Fraunces 600, 92px / 0.98,
  letter-spacing -0.03em, `#FFFFFF`, max 3 lines.
  Landing Spot: *"Six sheets of paper you keep moving from one end of the table
  to the other."*
- y 1120: Inter 700, 22px, letter-spacing 0.22em, uppercase, `#DDA63A`:
  `ENTRYWAY · THE LANDING SPOT`.
- **Hook rule, mandatory.** The hook line is an observed fact about this exact
  zone, drawn from `the_call.text` or `watch_for`, hand-trimmed to 16 words or
  fewer. Banned hook shapes: "Here's how to organize your X", "5 tips for X",
  "Do this to your X", any question, any imperative, any number-of-tips promise.
  A zone with no specific true failure to name does not get a video.

### 0.90 CUT to cream. The palette flip is the motion.

### 0.90–4.20 WHAT DONE LOOKS LIKE (cream)
- y 300: Fraunces 600, 56px, `#2B2622`: "What done looks like."
- y 420 down: `done_looks_like` decomposed into 3–5 count chips, stacked, left
  edge x 84. Chip: white fill, 1.5px `#E2D8C4` border, radius 999px, padding
  18px 32px, gap 18px. Numeral Inter 800 52px `#BC4B2A`; noun Inter 700 46px
  `#2B2622`.
  Landing Spot: `1 tray` / `1 upright folder` / `< 10 sheets` / `bare on both sides`.
- Chips land one per 0.45s: 8px upward move over 3 frames, no fade, no scale
  bounce. Once landed, a chip never moves again.

### 4.20–5.20 THE TIME PRICE (cream)
- Full-bleed honey band `#DDA63A`, y 860–1030.
- Inter 800, 54px, `#2B2622`, centred: `30–45 minutes · one session`, from
  `session`. Held static 30 frames. This kills the "that's my whole Saturday"
  objection before the steps arrive, which is why it sits at 4s and not at the end.

### 5.20–17.20 THREE MOVES (cream), 4.0s each
Default passes Sort, Straighten, Standardize. Per-zone override allowed; never
more than three, because six is a lecture.
- y 200–232: the six-S spine. Six bars, 152px wide, 6px tall, radius 999px, gap
  12px, from x 84. Inactive `#E2D8C4`. Active bar fills left to right over 10
  frames in its ramp colour: `--s1 #CB4B36`, `--s2 #BC4B2A`, `--s3 #D98A2B`,
  `--s4 #DDA63A`, `--s5 #6E8B5B`, `--s6 #4E7A57`. Completed bars stay filled.
  Progress bar and brand mark in one object.
- y 300: Inter 700, 24px, letter-spacing 0.22em, uppercase, `#BC4B2A`: `SORT`.
- x 84, y 380–1400, width 820: the instruction, Fraunces 600 62px / 1.10,
  `#2B2622`, revealed word by word (§3). 20 words maximum, hand-trimmed from the
  `passes` paragraph. Never paste the raw paragraph.
  Landing Spot / Sort: *"Every piece of mail gets a verdict — act, file, or
  recycle — before anything goes back on the surface."*

### 17.20–20.20 THE STANDARD (deep ground)
- Cut to deep. x 84, y 700: 4px honey rule, 200px wide.
- y 760: Newsreader 400 italic, 58px / 1.28, `#EDE4D2`, word-by-word reveal.
  Text = `leave_behind.standard`.

### 20.20–22.60 THE TRIGGER (deep ground, no cut)
- On one frame the standard lifts to y 520 at 46px. y 800: Inter 700 44px
  `#FFFFFF`, word by word: `leave_behind.trigger`.

### 22.60–24.00 END CARD (cream), static 42 frames
- y 700: `6S Success`, Fraunces 600 64px, `#2B2622`.
- y 790: 3px terracotta rule, 120px wide.
- y 840: Inter 600 34px `#6A625A`: `The full method, free · 6s-success.com`.
- y 900: Inter 600 30px `#BC4B2A`: the zone slug.
- No "follow for more", no subscribe animation, no arrow pointing at platform UI.

**Optional opening module — THE REVEAL.** For the 11 zones and rooms that own a
before/after diptych, replace 0.00–0.90 with a 2.2s reveal and shorten the three
moves to 3.6s each to hold 24s. BEFORE half filled to frame, held 1.3s, with
`before` in Inter 700 26px lowercase at x 84 y 1360 and the hook line over a
`#22323C` 82% plate; hard vertical wipe left to right over 8 frames to the AFTER
half; hold 0.6s with `after`. The wipe is the hook. No zoom on either half.

---

## 3. Captions — the karaoke system

Phil asked for highlighted word-by-word captions. Here **the captions are the
typography**, not a strip bolted underneath. There is never a headline and a
caption saying the same thing at two sizes, because that is the template look.
Every text beat is revealed by the same engine.

**Rendered in Chromium, not libass.** Our brand fonts are woff2, which libass
cannot load, and libass cannot draw rounded highlight chips. Chromium does both
and already renders the card fronts. Captions are baked into the frame PNGs.

- Faces: Fraunces 600 for hook and instruction lines; Inter 700 for label and
  trigger lines; Newsreader 400 italic for the standard.
- Sizes: 92px hook, 62px cream instruction, 44–58px deep beats. **Minimum size
  anywhere in any format: 38px.** Below that it is unreadable on a phone at
  arm's length.
- Line box: x 84, width 820, max 3 lines, max 26 characters per line, line-height
  1.10 display / 1.28 serif.
- Reveal: words appear one at a time and stay. Future words are not shown at all —
  greyed-out future text is a lyric video. Revealed words stay full-opacity ink,
  never dimmed.
- Visible at once: everything revealed in the current group, capped at 3 lines.
  When a fourth line would be needed the block clears on one frame and restarts.
  Effective simultaneous load 6–9 words.
- Active word: rounded chip behind the word. Fill `#BC4B2A`, radius 10px, padding
  6px 14px, text `#FFF7EC`. The chip moves on a hard cut, one frame, no tween, no
  scale. On deep grounds the chip is `#DDA63A` with `#22323C` text.
- Over imagery only: `#22323C` plate at 82% opacity behind the block, radius 18px,
  padding 20px 26px, plus `text-shadow 0 2px 0 rgba(43,38,34,.35)`. **No white
  stroke, ever** — stroke is the loudest tell of a generated short.
- Over flat brand grounds: no plate, no shadow. A plate over flat colour looks
  like a widget.
- Timing, deterministic from authored text, no ASR needed:
  `duration_ms = max(380, 62 * len(word))`, `+180` if the word ends a sentence,
  `+120` for numerals and chip values.

**Platform safe margins, real numbers at 1080x1920.**

| Platform | Top reserved | Bottom reserved | Right reserved | Left |
|---|---|---|---|---|
| TikTok | 130 | 500 | 260 | 40 |
| Reels | 220 | 420 | 220 | 40 |
| Shorts | 180 | 380 | 180 | 40 |
| **Union safe stage (design to this)** | **220** | **500** | **260** | **84** |

All type lives inside x 84–820, y 220–1420. The end-card block sits at y 700–940
so it survives every crop. Nothing meaningful goes below y 1420 or right of x 820,
which is why the line box is 820 wide and not 912.

---

## 4. Voice — no voice. Silent by default.

**Decision: no TTS in any of the 264 videos.**

The two available voices are Microsoft David Desktop and Microsoft Zira Desktop,
the SAPI5 concatenative voices, not the Windows 11 neural voices. They mispronounce,
they flatten clause boundaries, and within two sentences the listener knows a machine
is reading. The brand's entire claim is that a calm, competent person is telling you
what to do in your own house. A 2005-era robot delivering "the surface holds the tray
and the folder and nothing else" falsifies that claim in the medium that carries it.
**A robotic voice is worse than no voice for this brand**, and not marginally.

"Most short form is watched muted" is the supporting argument, not the argument.
Muted viewing means silence costs us little; the brand argument means TTS costs us
a lot. Both point the same way, so the decision is not close.

**Implementation:** every master carries a real but silent audio track —
`-f lavfi -i anullsrc=r=48000:cl=mono -c:a aac -b:a 128k -shortest` — so no platform
flags a missing stream and no player shows a broken audio state.

Do not fill the silence with a generated pad, drone, or synthesised tone. Anything
we can synthesise without a music library sounds like a stock-music placeholder,
which is worse than silence.

**Upgrade path, not a dependency:** Phil recording 24 seconds of guide track on a
phone beats both options. The beat map already carries word timings, so re-timing to
a recorded read is a manifest change, not a redesign.

---

## 5. Source imagery, per format

| Format | Imagery used | If it does not exist |
|---|---|---|
| A Zone Reset | None required. Type, the friction gauge SVG, the six-S spine. Optional: the 11 diptychs, the 5 entryway heroes, matching room boards, as the opening module. | Runs pure type. 109 of 114 will. This is the designed case, not a degraded one. |
| B Room Tour | Room diptych (9 rooms) as the reveal; zone-map overheads (`ch31-image02`, `ch34-image02`, `ch39-image02`) under the zone-list beat, numbers re-typeset in brand type. | The 11 imageless rooms run the pure-type beat map: room `intro` as hook, zone names as chips. |
| C Card Draw | The 90 rendered card fronts and backs. Card shown whole once, then only its photo band. | n/a, all 90 exist. |
| D The Answer | None. Pure type. Optionally one of the 13 site photographs where genuinely relevant. | Runs pure type. |

**Card photo band extraction (Format C).** Do not zoom into the card's small print;
rasterised 11px body text blown up is the cheapest look available. Crop the annotated
photograph band and re-typeset the callouts from `build/cardtext/batch-0*.json` in
brand type. The band is roughly x 8–752, y 185–612 on a 760x1055 front, but card
types differ, so detect it: OpenCV Laplacian variance over 40px row strips, take the
largest contiguous run of high-variance rows — photograph rows score far above the
flat cream and orange panels. Fall back to the fixed crop when detection is
ambiguous, and log every card that falls back.

---

## 6. Formats B, C, D beat maps (same engine)

**B Room Tour, 16s.** 0.0–2.2 reveal module, or type hook on deep. 2.2–5.0 the
room's job in one Fraunces line from `intro`. 5.0–10.0 the zone list: one chip per
micro zone landing 0.5s apart, over the zone map if it exists, else cream.
10.0–14.0 "Start with ___", naming the room's first zone from the `Where to start`
tip plus its `session` time. 14.0–16.0 end card.

**C Card Draw, 18s.** 0.0–1.2 the whole card, 620px wide, centred on deep
`#22323C`, drop shadow `0 30px 70px rgba(0,0,0,.45)`, static — it must read as a
physical object, so no spin, flip, or shimmer. 1.2–2.6 hard cut to the photo band
filled to frame, karaoke line = `objective` trimmed to 16 words. 2.6–12.6 five
callout beats at 2.0s: photo band held, callout label Inter 800 46px in a terracotta
chip at y 1180, callout body Fraunces 600 54px above it, re-typeset from JSON.
12.6–15.6 `home_quest_challenge` on cream as three chips. 15.6–18.0 end card
carrying `next_card.title` — the series hook is the next card, and it is real.

**D The Answer, 20s.** 0.0–1.4 the question exactly as a person asks it, deep
ground, Fraunces 92px. 1.4–5.0 the direct answer in one sentence on cream. The
answer arrives by second two, which is the AEO contract and the retention contract
at once. 5.0–16.0 three supporting points at 3.6s, six-S spine only for method
content. 16.0–20.0 end card with the article URL.

---

## 7. Build pipeline

1. `ops/build_video_manifest.py` reads `content.json`, `entryway-cards.json`,
   `cardtext/*.json` and `room-images.json`, emitting one JSON manifest per video:
   format, slug, ground per beat, every string pre-trimmed, word timings computed,
   imagery paths resolved or null.
2. `ops/video/<format>.html` renders a manifest at a **state index**, not a
   timestamp: `?m=<manifest>&s=<n>`. Deterministic, no animation clock.
3. Headless Edge screenshots each distinct visual state at exactly 1080x1920. A
   24s Format A has roughly 90 states, one per revealed word plus beat changes,
   not 720 frames. About 32s of screenshotting per video; 264 videos in ~2.5 hours
   single-threaded.
4. ffmpeg builds from a concat list with per-state durations, then layers the only
   continuous motions as filters: gauge sweep, chip rise, spine fill, and the one
   wipe. Everything else is a still held for its duration.
5. Encode: `-c:v libx264 -preset slow -crf 19 -profile:v high -level 4.1
   -pix_fmt yuv420p -g 60 -movflags +faststart`, plus the silent AAC track.
6. Output to `build/video/<format>/<slug>/`: `master.mp4`, `thumb.jpg` (frame 0),
   `poster.jpg` (end card), `caption.txt` (platform description with canonical
   URL), `manifest.json`.

---

## 8. What will look cheap, and how this spec prevents it

**1. Continuous Ken Burns drift on stills.** A slow endless push on a still image
is the universal signature of generated filler, and with 150 images and 264 videos
it is the tempting default. *Prevention:* `zoompan` is banned on every typographic
frame; on imagery, motion is one decisive move — a cut, an 8-frame wipe, or a
6-frame push — never a continuous drift. Hard rule: **at most one moving element
per beat, and most beats have none.** Stillness reads as confidence.

**2. White-stroked all-caps captions that bounce.** Outlined Impact-style text,
scale-pop word highlights and rainbow keyword colouring are what the eye now reads
as auto-generated. *Prevention:* brand faces only, sentence case, no stroke
anywhere, a chip highlight that cuts rather than tweens, no scale animation on any
text, no fades. The caption system is the site's own type system at video scale.

**3. Template recognition across 264 videos.** The third identical layout tells the
viewer a machine made all of them. *Prevention:* the hook line must be an authored,
zone-specific observed fact — the banned hook shapes in §2 exist precisely to stop
114 videos opening the same way. The six-S ramp colour, the chip values, the time
price and the ground sequence all vary per record, and Format A's three passes are
overridable per zone. A zone with nothing specific and true to say gets no video
rather than a filled template.

**Fourth, named because it is the one people forget:** robotic narration. See §4.
Silence.

---

## 9. First two to build

**1. `site/zones/entryway-the-landing-spot.html` — Format A, pure type, no
imagery.** The honest worst case: no hero photo, no diptych for the zone itself,
nothing but words. If Format A holds attention here it holds for the other 109
imageless zones, and the whole spec turns on that. It is also our richest record:
`the_call` yields a genuine hook ("the six sheets of paper you keep moving from one
end to the other"), `done_looks_like` decomposes cleanly into four count chips, and
the trigger is concrete. The entryway is the room the book tells people to start
with, so the traffic it earns lands on the page we most want entered. Build a
second cut of the same zone using the `ch31-image01` diptych opening, so the
imagery module can be measured against pure type on identical copy instead of
argued about.

**2. Card EE-001, "Amazon Delivery" — Format C.** Its `cardtext` record is fully
populated: five callouts, objective, game effect, quest challenge, progress tracker,
and a real `next_card` pointing at EE-002 Rainstorm. It exercises every beat with no
gaps to paper over. Its front carries the clearest annotated photo band in the deck,
making it the right first test of the OpenCV band detection the other 89 depend on.
And the scenario needs no setup: a package on the floor by the door is something the
viewer has looked at this week.

Build those two, measure three-second retention and completion, and do not start the
remaining 262 until both clear.
