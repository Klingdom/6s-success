# 6S Success Media Operations Plan

Photographs, line drawings, diagrams and video, produced at a consistent
professional standard and delivered in the right format for every platform.

**Owner:** Claude (autonomous) · **Approval gates:** Phil
**Written:** 2026-08-31

---

## 1. Where we actually are

| Fact | Value |
|---|---|
| Image tags across the site | 313 |
| Hero images wired and verified against recorded verdicts | 110 |
| Prompt generation tooling | `ops/build_image_prompts.py`, `build_card_prompts.py`, `build_all_prompts.py` |
| Style control | `ops/image_style.py`, House Style Bible, per-figure self-contained prompts |
| Review pipeline | `ops/review_heroes.py` with `hero-verdicts.json`, `card-hero-verdicts.json` |
| Local generation | `ops/image_local.py` |
| Video tooling | `ops/video.py`, `video_zone.py`, `video_narrated.py`, `render_all_narrated.py`, `build/video-format-spec.md` |
| Source photographs | `build/heroes/`, gitignored, not present in CI |
| Video series produced | 114 of 114 zones, silent and narrated, both orientations: 456 files |
| Narration | resolved. edge-tts neural voice (en-US-AvaNeural), narration drives the timing |
| Captions | 342 SRT files; every video has one |
| Where finished video lives | `Desktop/6s-success-videos`, NOT git. Verified by `ops/verify_media_delivery.py` |
| Published | 12 on youtube.com/@6SSuccess |

**The honest summary.** Both pipelines now produce. The gap is no longer
production, it is publication: 456 videos exist and 12 are public, so 97% of the
work sits on a disk where no customer can reach it. Nothing is blocked on
tooling or on a decision.

**Narration was never actually blocked.** This plan said for weeks that video
was waiting on one decision about narration, because Windows SAPI sounds
robotic. That was true of SAPI and false as a conclusion: Microsoft's neural
voices are free, natural, need no account and needed no decision from Phil. The
cost of that wrong conclusion was the whole video stream standing still while
being reported as blocked. When something is reported blocked on a decision,
check that the alternatives were actually enumerated.

**Rendered video is a build artifact and is not in git.** It was 794 files and
785 MB of tracked MP4; `.git` reached 1.1 GB and every clone dragged the whole
history. Untracking it on 3 September nearly destroyed it: `git rm --cached`
records a real deletion, and when that commit was rebased onto an origin that
still tracked the files, git removed 377 of them from the working tree. They
survived only because a copy had been made to the Desktop twenty minutes
earlier. Two rules came out of that: the renderer now copies to the Desktop as
part of rendering rather than as a step someone remembers, and the hourly
check-in reports any file that exists in only one place.

## 2. The problem this plan solves

Three failure modes have already cost us:

1. **Drift.** Generating chapter images in a long chat produced steadily
   diverging style. Fixed by a frozen House Style Bible plus self-contained
   per-figure prompts in a fresh context with an anchor image.
2. **Unreviewed output.** Images shipped with baked-in em dashes, fake QR codes,
   garbled text and invented logos. Fixed by recording a verdict per image and
   refusing to wire anything without one.
3. **Format sprawl.** One master asset used everywhere at the wrong dimensions,
   so it is heavy on mobile and cropped wrong on social.

This plan makes all three structurally impossible rather than a matter of care.

## 3. Image classes and their standards

### 3.1 Hyper-realistic photographs

**Use for:** room heroes, before and after pairs, product in context, the moment
a zone starts working.

**Standard.** A real home, not a showroom. Lived-in surfaces, honest light,
believable clutter in the "before". Natural window light, no studio rig look. No
brand marks, no readable text baked into the image, no invented logos, no faces
unless we hold the release.

**Believability rule for before and after.** The "after" must be reachable in
the time the quest claims. An after that is obviously a different, emptier house
destroys trust faster than a mediocre photograph does.

**Technical master.** 3000 px on the long edge, sRGB, 8-bit, lossless master
retained in `build/heroes/` and never overwritten.

### 3.2 Line drawings and diagrams

**Use for:** zone layouts, process flows, the six-S signature, before and after
schematics, anything where a photograph carries noise instead of meaning.

**Standard.** Single consistent stroke weight, the site's ink colour, terracotta
only as the accent that carries meaning, generous white space, no decorative
flourish. Every label must be real type set in the page, not drawn into the
image, so it stays translatable, searchable and legible at any size.

**Format.** SVG wherever the drawing is vector in nature. This is the biggest
quality and page-weight win available to us and it is currently underused.

### 3.3 Instructional and product images

**Use for:** what a tool looks like, what "done" looks like, what to buy.

**Standard.** Plain ground, one subject, consistent angle across a set so a
person can compare them. No aspirational styling that misrepresents the object.

### 3.4 What we never produce

Decorative filler, stock-looking business imagery, fabricated before and after
results, imagery implying an outcome we have not observed, or any image that
depends on baked-in text to make sense.

## 4. The production pipeline

Every image passes through five stages and none may be skipped.

1. **Subject.** Declared in `hero-subjects.json`. An image with no declared
   subject does not get made.
2. **Prompt.** Generated, self-contained, carrying the frozen style spec, in a
   fresh context with the anchor image. Never in a long thread, because that is
   what produced the drift.
3. **Generate.** At least three candidates.
4. **Review and verdict.** Recorded in `hero-verdicts.json` against a fixed
   checklist: no text artefacts, no invented brands, believable, on style,
   correct subject, correct aspect ratio. A verdict is a record, not an opinion.
5. **Wire.** Only a verdict-carrying asset may be wired. `ops/preflight.py`
   already refuses otherwise.

**The rule that makes this work:** the generator and the reviewer are separate
steps with a written artefact between them.

## 5. Delivery formats

One master, many derivatives, generated rather than hand-cut.

### Web

| Purpose | Format | Sizes |
|---|---|---|
| Hero and inline | AVIF first, WebP fallback, JPEG last | 480 / 800 / 1200 / 1600 wide |
| Line art | SVG, gzipped | single file |
| Delivery | `srcset` with explicit `width` and `height` | prevents layout shift |

AVIF and WebP are not optional. At our page weights they are the difference
between a fast mobile page and a slow one, and mobile is most of the audience.

### Print

300 dpi CMYK-safe derivative for the book, the manual and the card decks,
generated from the same master so print and web never diverge.

### Social and video platforms

| Platform | Aspect | Resolution | Notes |
|---|---|---|---|
| YouTube main | 16:9 | 1920x1080, 4K master | chapters, sidecar SRT |
| YouTube Shorts | 9:16 | 1080x1920 | under 60s, hook in the first 2 seconds |
| Instagram feed | 4:5 | 1080x1350 | the tallest feed format, most screen |
| Reels and TikTok | 9:16 | 1080x1920 | safe margins for platform chrome |
| Pinterest | 2:3 | 1000x1500 | highest intent surface for this category |
| Facebook | 1:1 and 16:9 | 1080x1080 / 1920x1080 | |
| Email | 16:9 | 1200 wide | under 200 KB |

**Rule:** the 9:16 crop is composed, never auto-cropped from 16:9. An auto-crop
puts the subject's head out of frame and reads as careless.

## 6. Video operations

### 6.1 What we are making

114 zone videos, one per micro zone: what the zone is, what goes wrong, the six
passes, what done looks like. Two to four minutes each, plus a short vertical cut
per zone for Shorts, Reels and TikTok.

### 6.2 Format specification

- **Master:** 3840x2160, 24 or 30 fps held consistently, ProRes or
  high-bitrate H.264, sRGB / Rec.709.
- **Audio:** loudness normalised to -14 LUFS integrated, true peak below
  -1 dBTP. This is the streaming standard, and getting it wrong is the most
  common reason amateur video sounds amateur.
- **Captions:** burned in for vertical, sidecar SRT for horizontal. Vertical
  video is watched muted, so uncaptioned vertical is unwatched vertical.
- **Titles and lower thirds:** real type, site fonts, high contrast, safe
  margins.

### 6.3 Narration was never a blocker, and I was wrong to present it as one

**Corrected 2026-09-01.** I wrote that the entire 114-video stream waited on a
narration decision from Phil. That was wrong, and he said so: "you can do all
this, investigate and try everything before you come to me."

He was right. ffmpeg 8.1.1 with libass, zoompan, xfade and drawtext is installed
on this machine, and `ops/video_zone.py` already drives it. Proved rather than
argued: Landing Zone rendered to 1080x1920, 30 fps, 30.2 seconds, before this
paragraph was written. All 114 are now rendering.

Captions carry the instruction, so silent video is not a compromise here. It is
watched muted anyway, it is accessible by construction, and it costs nothing.
Voice can be added later to whichever videos earn attention. There is no
decision to wait for.

**The lesson is bigger than video.** I escalated a question I had not tried to
answer. Before anything goes on the owner's list again it has to survive one
test: have I actually attempted it and hit a real wall, or am I asking because
asking is easier than checking?

### 6.3b The original framing, kept because being wrong in public is the point

Windows SAPI narration sounds robotic and would undercut the brand on the one
channel where production quality is most visible.

| Option | Cost | Quality | Unblocks |
|---|---|---|---|
| **Captions only, no voice** | $0 | Good, and honest | **All 114 immediately** |
| Commercial synthetic voice | roughly $10 to $30/mo | Very good | All 114, after setup |
| Phil records | time | Best, it is the brand's own voice | Slowly |

**Recommendation: start captions-only and ship all 114.** Silent, well-captioned
instructional video performs well in this category because it is watched muted,
it is fully accessible by construction, and it costs nothing. Add voice later to
the videos that earn attention. Shipping 114 silent videos beats shipping 3
narrated ones.

**This is a decision I need from Phil, and it is the entire video stream.**

### 6.4 Accessibility, which is not optional

Captions on everything. Meaningful alt text on every image, describing what
matters rather than restating the caption. No information carried by colour
alone. Respect reduced motion. Contrast checked against WCAG 2.2 AA.

## 7. Quality gates

These run in `ops/preflight.py` and block a ship, exactly as the existing
image-coverage gate does.

1. No image wired without a recorded verdict. **Already enforced.**
2. Every image has non-empty, non-duplicate alt text.
3. Every image has explicit width and height.
4. An AVIF or WebP derivative exists for every raster asset over a threshold.
5. No asset exceeds the weight budget for its role.
6. Every video has captions before it is published anywhere.

Gates 2 to 6 are to be built. Each is small, and each prevents a class of defect
we have already shipped at least once.

## 8. Cadence

| Cycle | Output |
|---|---|
| Each cycle | one room's images fully produced, reviewed and wired |
| Each cycle | derivatives regenerated for anything new |
| Weekly | 3 to 5 zone videos, captioned, in all formats |
| Monthly | audit: unused assets, missing verdicts, weight regressions |

## 9. What is blocked on Phil

| # | Decision | Why it matters |
|---|---|---|
| 1 | **Narration: captions-only, paid voice, or record it yourself** | The entire 114-video stream waits on this. Captions-only costs nothing and unblocks today. |
| 2 | Budget for a commercial voice, if that is the choice | roughly $10 to $30/mo |

Nothing else in this plan needs an answer.

## 10. What I will do next without being asked

1. Build quality gates 2 through 5, since each blocks a defect already shipped.
2. Generate AVIF and WebP derivatives with `srcset` for the 313 existing images,
   which is the largest available mobile performance win.
3. Convert diagrams that are vector in nature from raster to SVG.
4. Produce the first room's video set captions-only as a working sample, so the
   narration decision is made against something real rather than in the abstract.
