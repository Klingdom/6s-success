# Media plan: images and video, 2026-09-07

**Written by:** ux-frontend, on Phil's standing direction *"keep prioritising
improvement of image and video generation."*
**Scope:** what to make, in what order, so that the moment Gemini billing is on,
generation runs unattended and produces work nobody has to redo.
**Method:** every claim below was checked by opening the actual file, the
image, the MP4 frame, the SRT, the live URL, not by reading a filename or a
verdict record. Where I could not check, it says so.

This is a plan, not a change. Nothing in the repository was edited except this
file.

---

## 0. The one-paragraph version

The pictures are the constraint, and they are the constraint for a reason no
prompt can fix: **every hero image on this site and in the deck was made by
Stable Diffusion 1.5 at 768x576 on the local GPU.** That model cannot compose a
scene from five named objects, which is why the approved "Key Station" hero
contains no keys. The written standard in `MEDIA-OPERATIONS-PLAN.md` asks for
3000 px masters; we are shipping 768. Meanwhile the correct card pipeline, a
textless photograph plus card text set in real type, is **already built and
already renders correctly**; the only thing wrong with its output is the
photograph inside the window. So the billing click does not buy "some images."
It buys the one input that finishes a pipeline that is otherwise complete.

Before that click there is about a week of work that is not blocked on it, and
most of it must happen **first** or the generated images will need redoing.
Chief among it: an accept test that a picture must pass to be published, which I
proved this morning can run **free, today, unattended**, the free tier refuses
to *make* images but happily *reads* them.

---

## 1. What I verified, including where the brief I was given is wrong

| Claim I was given | Verified? | What the files actually say |
|---|---|---|
| Image generation is billing-gated, not blocked | **Confirmed today** | I sent a real request to all three models this morning. All returned HTTP 429 with `limit: 0` on `generate_content_free_tier_requests`. Not an exhausted daily quota, a zero allowance. |
| 110 of 114 zone heroes exist, reviewed, live | **Partly** | `ops/hero-verdicts.json` holds **107 "ok" and 7 "no"**. 107 zone pages reference a hero. 110 slugs have derivative files on disk, so **3 rejected zones have 27 orphan files** no page uses. |
| Exactly 4 were rejected | **No, 7** | `OWNER-ACTIONS.md` 1b was itself corrected to 7 earlier today; the brief carried the stale 4. All 7 now have hand-written subjects. |
| EM-003 prints six callouts about keys over a photograph containing no keys, and passed review | **Confirmed, and it is worse than stated** | True of `build/heroes/entryway/EM-003.png`, verdict `"ok"`. I opened it: a cabinet, a mirror, a handbag. No keys, no bowl, no key hooks. **It is not true of the card face currently on the site**, which is a different, baked render that does show keys. Two different artefacts, both real, needing different fixes. |
| The Entryway card art folder holds 1,153 files | **Confirmed** | `site/assets/cards/entryway/`, 72 cards x 2 faces x 3 sizes x 3 formats, plus an index. 49 MB. |
| Two card faces carry garbled text and a fake QR block | **Garble confirmed. QR not found.** | I opened 12 faces. EM-005 and EM-006 fronts carry a garbled bottom band ("PHEE GUEST FRIENDLY aoaay", "Rably nay be equipped", "Ceobd Bnenony - Contnoos"). I did **not** find a QR-imitating block in the current shipped set; the review that reported it (`content/decks/reviews/review-card-images-canon.md`) was written against an older 35-image set. **Unchecked, not disproved**: 12 of 144. Item A5 closes this properly. |
| Eight card faces carry unsourced statistics baked into pixels | **Confirmed on 3 of the 12 opened** | EM-001 back prints a large badge "**7X LESS LIKELY TO BE TARGETED**"; EM-005 back "421,000 bacteria per step"; EH-004 back "over 2 pounds of mail per week". I fetched EM-001's back from **production** and hashed it, byte-identical to the repo copy. It is live now. |
| The written versions of those statistics were removed on 2026-09-06 | **False, and this is the most dangerous thing in this document** | `build/cardtext/`, the corpus that feeds the *new* card renderer, still carries **27 unsourced numeric claims**, 17 of them on cards shipped today. Including the exact string from the brief: EH-001, *"You can save 150+ hours per year."* 87 of 90 `did_you_know` lines were genuinely rewritten into defensible unquantified prose. 27 were not. **If we render the good pipeline today we would reprint 27 fabricated statistics in crisp, legible, unmissable type.** |
| 456 videos, 114 thumbnails, 12 published, blocked only on OAuth | **Confirmed, plus a defect nobody has reported** | All counts check out against disk and ffprobe. But **7 of the 12 videos already public carry a "full written steps" link that returns 404**, and 13 of the 114 metadata files do. That link is the entire mechanism by which a video sends anyone to the site. |

**Two further defects found that were not in the brief:**

- **412 mid-word truncated sentences across 113 of the 114 video descriptions.**
  Example, live on YouTube now: *"...print it small, and tape it inside the coat cu"*.
- **Nine cards with a recorded verdict of `"no"` are shipped and live**,
  EE-002, EH-004, ES-007, ET-003, ET-004, EU-002, EU-004, EU-009, EU-011. The
  zone-hero pipeline gates on verdict *value*; the card pipeline
  (`ops/split_deck_cards.py`) never reads a verdict at all.

---

## 2. The architecture decision that determines everything else

There are two card pipelines in this repository and only one of them should
survive.

**Pipeline A: what is live.** `ops/split_deck_cards.py` takes 89 finished card
sheets generated wholesale by a text-to-image model on Phil's Desktop and slices
them into web derivatives. **Every word on those cards is pixels.** That is the
sole and sufficient cause of: the garbled bottom bands, `HŒUSE` on EM-002's
subheadline, the ghost word "FRONT" bleeding above the header on EM-007 and
EM-012, the 7X burglary badge, and every dangling card code, EM-001's back
points at EP-001 and EX-002, and **neither the EP-001 card nor the entire EX
family exists**. None of it is editable. Seventeen cards are already withheld
from the deck for exactly these reasons, which is why ER-001, the deck's own
contents card, indexes twelve micro zones when the box holds ten.

**Pipeline B: what is right, and what already works.**
`ops/build_card_template.py` composes a card from a **textless** hero photograph
plus HTML/CSS type, and `ops/render_cards.py` photographs it in headless
Chromium behind a 7pt minimum-type gate and an overflow gate. **178 rendered
PNGs already exist in `build/cards-rendered/`.** I opened `EM-003-front.png`:
clean 5:7 trading card, 750x1050, real display serif, correct canon
("STRAIGHTEN", not "Set in Order"), no garble possible. The one thing wrong with
it is the photograph in the window, the keyless key station.

**So the decision is:** retire pipeline A, ship pipeline B, and spend the money
exclusively on textless hero photographs. Every text defect in the deck then
becomes a JSON edit costing nothing, and the accept test in section 4 has a
tractable job: judge a photograph, not a whole composed card.

The same logic applies to the room zone maps (section 6) and, less obviously, to
the videos (section 7).

---

## 3. NOT BLOCKED ON THE BILLING CLICK, do this first, in this order

Ordered so that nothing generated later has to be redone. Effort is for one
operator agent.

### A1. Fix the 27 unsourced numeric claims in the card corpus. Do this before anything renders.
- **What:** `build/cardtext/*.json`, rewrite or source all 27 `did_you_know`
  lines containing a digit. 17 sit on cards shipped today. The `claims` field
  already exists on the schema and is populated on exactly 3 of 90 cards.
- **Why:** CLAUDE.md section 8 forbids fabricated statistics outright. Today they
  are blurry pixels on a low-traffic gallery. The moment pipeline B renders they
  become crisp 12pt type on the product we sell. **The good pipeline would make
  the trust problem worse, not better,** and that is the definition of work that
  has to be redone.
- **Effort:** 3-4 h. 87 of 90 lines already model the right voice, so this is
  rewriting to a house pattern, not invention.
- **Acceptance:** zero `did_you_know` strings contain a digit unless the card's
  `claims` field carries a citation; a new `gate_card_numeric_claims` in
  `ops/preflight.py` fails the build otherwise. `gate_card_corpus` already bans
  "Set in Order", this is the same gate shape for numbers.
- **Blocked on billing:** No.

### A2. Withhold the live card faces that carry a fabricated statistic.
- **What:** extend `WITHHOLD` in `ops/split_deck_cards.py`, which already
  withholds 17 cards for canon and trademark defects, to cover every face whose
  pixels carry an unsourced number, then rebuild the gallery.
- **Why:** the 7X burglary badge is live in production right now; I fetched and
  hashed it. Under CLAUDE.md 0.2 a correctly reported customer-facing failure is
  fixed now, not next cycle. Withholding is the honest interim: the picture is
  kept back rather than a false claim shipped.
- **Effort:** 1-2 h, after A5 produces the full list.
- **Acceptance:** no card face served from `6s-success.com` carries a numeric
  claim, verified by re-fetching each from production rather than from the repo.
- **Blocked on billing:** No. The permanent fix is tier 1 in section 5.

### A3. Gate the card pipeline on verdict *value*.
- **What:** `ops/split_deck_cards.py` reads `ops/card-hero-verdicts.json` and
  refuses any card marked `"no"`. Add a preflight gate mirroring
  `gate_image_coverage`, which already does this correctly for zone pages.
- **Why:** nine rejected cards are live because the card path never asks. The
  zone path asks. One of the two is right.
- **Effort:** 2 h.
- **Acceptance:** the count of shipped card faces equals the count of approved
  ones, and preflight prints both numbers side by side whether it passes or
  fails.
- **Blocked on billing:** No.

### A4. Build the accept test. This is the keystone item.
Full specification in section 4. Summary: a checklist derived mechanically from
the card's own callouts (or the zone's own `done_looks_like`), answered as closed
yes/no questions by a vision model, with the answers stored as evidence rather
than a one-word verdict.
- **Effort:** 1 day for `ops/accept_image.py` plus the checklist derivation.
- **Acceptance:** run against the 202 existing heroes; `EM-003` must fail on
  "keys visible"; `entryway--landing-zone` must pass. **Both already verified by
  hand this morning**, see section 4.
- **Blocked on billing:** **No.** Free-tier image *understanding* works; only
  image *generation* is gated. This was the most useful thing I learned today.

### A5. Run the accept test over everything that already exists. Free, unattended.
- **What:** 114 zone heroes + 88 card heroes + 144 shipped card faces = 346
  images. For the card faces the questions are different: *does this image
  contain a numeric statistic? garbled or nonsense lettering? a block resembling
  a QR code? a brand mark?*
- **Why:** this replaces the twelve-per-page 320-pixel contact sheet that let the
  keyless key station through, and it settles the open questions in section 1,
  how many faces really carry statistics, whether the fake QR is still there,
  with measurement instead of a sample of twelve.
- **Effort:** 2 h to write the two question sets, then about 4 h unattended at
  the observed 30-60 s per image.
- **Acceptance:** a machine-readable table naming every image that does not
  depict its own subject and every face carrying a claim, with the specific item
  each one failed on. No image is described as "reviewed" without one.
- **Blocked on billing:** No.

### A6. Fix the 7 live YouTube 404s without touching OAuth.
- **What:** thirteen `location = /zones/<old-slug> { return 301 /zones/<real-slug>; }`
  blocks in `site/nginx/default.conf`. That file already uses exactly this
  pattern on lines 187-188.
- **Why:** seven of the twelve videos on the channel send every viewer who clicks
  the description link to a 404. The channel is the only traffic asset we own
  outright (GOALS.md O1) and its call to action is broken for 58% of it. Editing
  a published description needs the OAuth Phil has not given yet. A redirect on
  our own server needs nothing.
- **Effort:** 1 h including deploy.
- **Acceptance:** all thirteen legacy URLs return 301 to a 200, verified against
  production with curl, not against the repository.
- **Blocked on billing:** No. Not blocked on OAuth either.

### A7. Fix the description generator: 412 truncations and 13 wrong slugs.
- **What:** `ops/build_youtube_metadata.py` truncates each six-pass line mid-word
  and derives the zone URL from the video slug rather than from the page that
  exists. Regenerate all 114.
- **Why:** 113 of 114 descriptions contain a sentence that stops mid-word. 102 of
  these are unpublished, so fixing it now means they publish correct the first
  time; YouTube allows a later edit but that is 102 manual edits nobody will do.
- **Effort:** 2-3 h.
- **Acceptance:** zero pass-lines end without terminal punctuation; 114 of 114
  links resolve against `site/zones/`; a preflight gate checks both, so a
  regenerated description cannot silently break the link again.
- **Blocked on billing:** No.

### A8. Give the 144 card images in the deck gallery real alt text.
- **What:** `site/deck-gallery.html`, every one of 144 card images carries
  `alt=""`. The page is titled "Every card in the Entryway deck." The card code,
  type, title, tagline and callouts all exist in `build/cardtext/`.
- **Why:** the entire product gallery is invisible to a screen reader and carries
  no image SEO, on a site whose measured constraint is arrivals. It is also the
  cheapest content the accept test produces for free: the vision run in A5
  returns a literal description of each face.
- **Effort:** 2 h.
- **Acceptance:** 144 non-empty, non-duplicate alt strings naming the card and
  what its picture shows. This is quality gate 2 from `MEDIA-OPERATIONS-PLAN.md`
  section 7, still unbuilt since 31 August.
- **Blocked on billing:** No.

### A9. Put explicit width and height on the 159 images in `shop.html`.
- **What:** 159 of the 483 `<img>` tags on the site lack `width`/`height`, and
  **all 159 are on `shop.html`**, the highest commercial-intent page we own.
- **Why:** cumulative layout shift on the buying page. This is quality gate 3
  from the media plan, also unbuilt.
- **Effort:** 1 h.
- **Acceptance:** 483 of 483 images carry explicit dimensions, and a preflight
  gate keeps it that way.
- **Blocked on billing:** No.

### A10. Move the style source into the repository.
- **What:** `ops/generate_card_art.py` reads its frozen style prefix from
  `~/Desktop/6S-Success-Card-Decks/prompts/entryway-regeneration-prompts.md`,
  outside the repository, outside version control, outside CI.
- **Why:** this is a precondition for "runs unattended." If that file moves or
  changes, an overnight batch either dies or, far worse, drifts silently into a
  second visual identity, which the file's own comments say has already happened
  once on this project. The style hash is recorded per image, so drift would be
  *detectable*, but only after the money is spent.
- **Effort:** 30 min.
- **Acceptance:** `--check` reports "style src: found" from a repo path on a
  clean checkout with no Desktop present.
- **Blocked on billing:** No. **Must be done before the click.**

### A11. Fix the orphaned keyword chip in the narrated video renderer.
- **What:** at 00:60 of the Landing Zone film the caption reads *"Lift the tray
  out and wipe under it, then wipe the tray itself.* **Keys**". The zone-noun
  highlight chip is appended after the sentence instead of highlighting the word
  inside it. It appears in both orientations.
- **Why:** it reads as a non-sequitur on a film whose whole job is to be
  followable, and it is in all 114.
- **Effort:** 2 h; applies on the next render, which is coming anyway.
- **Acceptance:** the chip highlights an occurrence of the word within the
  sentence, or is omitted when the word does not occur.
- **Blocked on billing:** No.

### A12. Retarget loudness from -15 to -14 LUFS.
- **What:** measured across ten narrated films: integrated loudness -15.0 to
  -15.2 LUFS, true peak -1.1 to -1.3 dBTP. Extremely consistent, so
  normalisation is running; it is just aimed 1 LU low.
- **Why:** YouTube normalises down to -14 and never up, so every one of our films
  plays about a decibel quieter than everything around it. The media plan already
  specifies -14.
- **Effort:** 30 min, applies on the next render.
- **Acceptance:** integrated loudness within 0.5 LU of -14.0 and true peak below
  -1.0 dBTP, sampled across ten files.
- **Blocked on billing:** No.

### A13. Remove the 27 orphan derivative files for the three rejected zones.
- **What:** `home-office--printer-and-scanning-station`,
  `mudroom--family-hook-zone` and `nursery--crib-and-sleep-zone` each have nine
  derivative files in `site/assets/zones/` that no page references.
- **Why:** they ship inside the Docker image and they are pictures we decided not
  to publish. If one is ever wired by mistake it publishes a rejected image.
- **Effort:** 15 min.
- **Acceptance:** the count of asset stems equals the count of approved zones
  equals the count of pages carrying a hero. `gate_image_coverage` already
  compares three numbers; add this as the fourth.
- **Blocked on billing:** No.

### A14. Correct the two stale premises in the media documents.
- **What:** `ops/build_thumbnails.py` states as a design rule *"no photograph
  behind the type. There is no per-zone photography."* `ops/video_zone.py` states
  it is typographic because *"109 of the 114 micro zones have no photograph."*
  Both were true when written; 107 zones now have an approved picture.
  `MEDIA-OPERATIONS-PLAN.md` section 9 still lists the narration decision as the
  one thing blocking the video stream, which was withdrawn.
- **Why:** a design constraint that has expired keeps producing the design it
  chose. This has now happened twice in the same subsystem.
- **Effort:** 1 h.
- **Acceptance:** each docstring states the constraint *and the date it was last
  true*, and the media plan's "blocked on Phil" table lists only the two live
  gates: billing and YouTube OAuth.
- **Blocked on billing:** No.

**Section 3 total: roughly four to five working days, none of it waiting on
anyone.**

---

## 4. The accept test: how a picture that does not depict its own card stops passing

### Why the current one failed

`ops/review_heroes.py` builds contact sheets **twelve images to a page at 320
pixels wide** and records one word per image. At 320 px in a 4x3 grid the only
question a reviewer can actually answer is *"is this an entryway?"*, and the
keyless key station passes that question. The verdict was not dishonest; it was
an answer to the wrong question, asked at a resolution that could not support a
better one.

There is a second, deeper cause. The subject string for EM-003 reads: `"key
station, Location (Near Entry), Key Bowl (Home Base), Key Hooks (By User),
Outgoing Mail Slot, tidy and settled, everything in its place, in a home
entryway, warm wood and painted wall, daylight"`. That is five distinct objects
in a spatial arrangement. **Stable Diffusion 1.5 cannot do that**, and no prompt
makes it able to. I checked the obvious alternative explanation: the prompts are
*not* over CLIP's 77-token limit, roughly 48 tokens median for zone heroes, 53
for card heroes. The truncation bug `ops/image_style.py` was written to fix is
genuinely fixed. What remains is model capability. I could not run the exact BPE
count because the tokenizer download timed out, so treat those figures as a
proxy, not a measurement.

### The design

**1. The checklist is generated from the same record that prints the card.**
Every one of the 90 cards in `build/cardtext/` already carries a `callouts`
array, median 5, max 12, and those callouts are the numbered pins printed on
the card face. EM-003's are exactly: *Location (Near Entry), Key Bowl (Home
Base), Key Hooks (By User), Outgoing Mail Slot, Daily Catch-All Tray, Visual Cue
/ Reminder.* For zone heroes the equivalent source is `done_looks_like` in
`content/manual/source/content.json`, written for all 114 in countable terms:
*"One tray holding keys and sunglasses, one wallet and one phone per adult, a
single upright folder with fewer than ten sheets of paper standing in it..."*

This is the structural guarantee. **If the card prints six callouts, the image
must contain six things, and the test is built from the same field.** A picture
cannot pass while contradicting its own card, because the checklist and the
callouts cannot drift apart.

**2. The questions are closed and countable, never evaluative.** Not *"is this a
good key station?"* but *"is a key visible? true/false"*. The checklist has three
parts:

- `must_show`: 3 to 6 concrete, countable nouns. The first is the zone's primary
  object and is a **hard** fail.
- `must_not_show`: readable lettering, brand marks, human faces, any object that
  looks physically impossible or malformed. All hard fails.
- `contradicts`: the negative image of the standard. For the shoe zone that is
  *"shoes loose on the floor"* and *"more than six pairs visible"*. This is the
  category the old review had no way to express, and it is the one that matters
  most: a picture can contain every required object and still be showing the
  *before*.

**3. It runs free, today, unattended. Proved, not assumed.** Image generation
returns 429. **Image understanding does not.** I ran `gemini-3.6-flash` against
three heroes this morning:

```
EM-003 (approved "ok")        -> any_keys_visible:        false
                                 key_bowl_visible:        false
                                 hooks_with_keys_on_them: false
entryway--landing-zone        -> a tray: true, keys: true, a wallet: true
primary-bathroom--medicine-   -> any object physically impossible
  cabinet-or-wall-storage        or malformed: true
```

The test discriminates correctly on the exact failure this plan exists to
prevent, and it independently caught the levitating sink in the bathroom hero
that no human reviewer flagged. Latency was 30-60 s per image, so 346 images is
a single unattended afternoon at zero cost.

**4. Two passes, order shuffled, must agree.** The bathroom run also showed the
model is permissive on category words: it answered `true` to "medicine bottles or
pill packets" for a cabinet I read as toiletries. So the checklist must use
discriminating nouns: *"a pill bottle with a white child-resistant cap"*, not
*"medicine"*, and a single yes/no is evidence, not a gate. Two runs with the
item order shuffled; disagreement escalates to a human.

**5. The verdict record becomes evidence, not an opinion.** `hero-verdicts.json`
today stores `{"sha": ..., "verdict": "ok"}`. It should store the sha, the
checklist it was judged against, and the answer to every item. Then "EM-003
passed review" becomes a falsifiable statement somebody can check, and the file
explains *why* rather than merely asserting.

**6. It closes the loop inside the generator, which is what makes the batch
unattended.** `ops/generate_card_art.py` currently calls `verify()`, which checks
only that the image is at least 512 px and has a standard deviation above 12,
that it is not blank. `ops/review_deck_art.py`'s own docstring already names that
gap: *"None of those can tell a correct card from a garbled or mismatched one."*
Wire the accept test in as the second half of `verify()`: on failure, regenerate
with a new seed, up to three attempts, then park the image and report it. **A
failed generation then costs four cents and no human attention.** That is the
difference between "the batch ran overnight" and "the batch ran overnight and the
output is usable."

**7. Human review still happens, but only on what the machine passed, one image
per screen at full resolution.** The reviewer's job stops being *find the broken
ones among 144 thumbnails* and becomes *is this beautiful, and does it feel like
a real home*. That is a judgement a person is good at and a model is not, and it
is the only question a person should be asked.

**Acceptance for the whole item:** replaying the test against the historical
record must reproduce known outcomes, EM-003 fails, the garage tool wall fails
`contradicts` on "no labels or shadow outlines marking where each tool belongs",
`entryway--landing-zone` passes, **before a single paid image is generated.**

---

## 5. Priority order for regeneration, and why

The moment billing is on, this is the queue. It is ordered by customer harm
removed per dollar, not by volume.

**First: the 89 Entryway card heroes.** Textless, 5:7-croppable, 2K. First for
four compounding reasons. The deck is the flagship product and its picture is on
`shop.html`. Seventeen of the 89 cards are withheld from the box today purely
because of defects baked into pixels, so a buyer receives an incomplete deck
whose own contents card indexes twelve zones when ten are present. The receiving
pipeline is finished and proven, 178 cards already render correctly. And it is
the smallest job on the list.

**Second: the 7 rejected zone heroes.** All seven have hand-written subjects
waiting. Seven pages are text-only today, correctly so: the picture was withheld
rather than a wrong one shipped under a caption claiming it shows the finished
state. Cheapest possible completion of an existing surface.

**Third: the 11 room pages with no photography.** See section 6, a different job
from a hero, and it should not be treated as one.

**Fourth: re-shoot the 107 approved zone heroes.** The largest item and
deliberately last, because until the accept test has run over the existing 107 we
do not know how many genuinely need it. My sample suggests a lot: the garage tool
wall has melted, anatomically impossible tools and no organising system at all;
the medicine cabinet is a showroom containing no medicine, which the media plan's
own standard forbids ("a real home, not a showroom"); the shoe zone shows roughly
eighteen pairs of boots strewn across a floor. **A5 turns that sample into a
list.** Re-shoot what fails and what the videos will magnify, not all 107 by
default.

**Fifth: nothing.** A second deck is explicitly not planned until the free
Entryway deck produces evidence (`ROADMAP-2026-2029.md` section 4), and this plan
does not reopen that.

### One specification change that must be decided before any of it runs

**Aspect ratio.** Every hero is 768x576, 4:3. The vertical video pads that into
9:16 with an ugly blurred letterbox top and bottom, visible in the frame I
pulled from the photo-led shoe zone clip. The media plan forbids auto-cropping
16:9 into 9:16 for exactly this reason; auto-*padding* 4:3 is the same mistake
wearing a different hat. So each hero destined for video must be generated as
**two composed frames** from the same scene description, not one master and a
crop: a 3:2 or 4:3 for the page and card, and a composed 9:16 for video and
Reels. That roughly doubles the count for anything used in video, and it is the
difference between a vertical film that looks made and one that looks converted.

### What the money actually buys

Prices below are the ones recorded in `ops/generate_card_art.py` for
`gemini-3.1-flash-image`: $0.045 at 0.5K, $0.101 at 2K, noted there as fetched
2026-09-04. **I did not re-fetch them today; treat them as four days old.**

| Tier | Finals | With accept-test retry (~1.4x) | At 2K | At 0.5K |
|---|---|---|---|---|
| 1. 89 card heroes + 7 zone rejects | 96 | 134 | **$13.53** | $6.03 |
| 2. 11 room pages, 2 images each, + Family Room top-up | 24 | 34 | $3.43 | $1.53 |
| 3. Re-shoot 107 zone heroes, two compositions each | 214 | 300 | $30.30 | $13.50 |
| **All three** | **334** | **468** | **$47.26** | **$21.06** |

At the fixed three-candidates-per-image the media plan currently specifies, the
same programme is 1,002 requests and $101.20 at 2K. **The accept test is what
makes adaptive retry safe, and it roughly halves the bill**, because you only
pay for a second candidate when the first one failed a test, rather than always
paying for three and picking by eye. Suggested escalation policy: flash for
candidates, and only escalate an individual image to `gemini-3-pro-image` after
it has failed the accept test three times on flash.

**So: your thirty dollars finishes the product.** Tier 1 removes the fabricated
statistics from the deck permanently, releases the 17 withheld cards, and makes
the deck's own contents card true. Tier 2 fills eleven blank room pages. Tier 3,
the largest and least urgent, brings the 107 existing heroes up to the written
standard. Roughly a hundred dollars covers everything at the highest quality
setting with no adaptive retry at all. **None of these is a monthly run rate;
they are one-time programme costs**, and the accept test means an image is paid
for once.

---

## 6. The eleven room pages with no photography

Measured, not assumed: **eleven of the twenty room pages contain zero images**,
garage, guest bathroom, hall closet, home office, laundry room, mudroom, nursery,
patio or deck, primary bathroom, stair landing, workshop. The other nine carry
between one and seven, and the distribution is lopsided: Dining Room has seven,
Family Room has one. The nine have pictures because the book drew those chapters.
The eleven have no source to import from.

**These should not be filled with hero photographs.** I opened
`ch31-image02.jpg`, the Entryway page's zone map, and it is the best image in the
estate: an overhead plan of the room with its five zones outlined, numbered and
labelled, and a line beneath reading *"one room, five small jobs."* It answers
the question a room page exists to answer, *what can I improve here?*, which no
photograph of a tidy room can. And it maps one-to-one onto the five entryway zone
pages, so it is navigation as well as illustration.

**So the job for each of the eleven is two images, not one:**

1. **A zone map.** Generate the room scene *textless* at 2K; set the numbers,
   labels and zone outlines as **SVG over the top**, drawn from the same zone list
   that generates the room page's links. This is `MEDIA-OPERATIONS-PLAN.md`
   section 3.2 verbatim: *"every label must be real type set in the page, not
   drawn into the image, so it stays translatable, searchable and legible at any
   size"*, and it is the single largest quality, accessibility, page-weight and
   internationalisation win available anywhere in this estate. It also makes the
   map maintainable: when a zone is renamed the label changes and the picture does
   not need regenerating.
2. **A before-and-after pair**, subject to the media plan's believability rule:
   the after must be reachable in the time the page claims, in the same room, with
   the same furniture. An after that is a different, emptier house destroys trust
   faster than a mediocre photograph does.

**Effort:** 1 day to build the SVG overlay component and wire it to the existing
zone data; then 22 generated bases behind the click. **The overlay component is
not blocked and should be built first**, because it is also the retrofit path for
the nine rooms whose maps currently have their labels baked in.

**Acceptance:** all 20 room pages carry a zone map whose labels are selectable
text, keyboard-reachable, and linked to that zone's page; each map's zone count
equals the number of zone pages for that room; alt text describes the room and
names the zones.

**Blocked on billing:** the overlay component, No. The 22 room bases, Yes.

---

## 7. Should the video style change now that we know what a zone page looks like

**Yes: and the tool to do it is already written, and the premise for the current
style has already expired.**

`ops/video_zone.py`'s docstring says it is typographic *"because 109 of the 114
micro zones have no photograph and there is no stock library on this machine."*
That was honest when written. 107 zones now carry an approved picture.
`ops/video_zone_photo.py` already exists, says so in its own docstring, and
reports `114 zones / 107 with an approved picture / 7 held back / 2 already
built` when run.

I pulled frames from both and the difference is not close.

**The current narrated film**, sampled at 3 s, 20 s, 60 s and 110 s, is a
text-only slideshow. The typography is genuinely good and the six-S progress
spine along the top is a real visual control. But at 20 s the entire 1920x1080
frame holds an eyebrow, a title and an amber bar reading "30-45 min", with the
bottom 45% empty; at 60 s a single sentence sits in a field of cream. Median
length is **126 seconds of that**. On a feed it holds attention for about a
second, and on YouTube the first three seconds, the hook, are a static title
card.

**The photo-led vertical**, sampled at 8 s, is full-bleed image with a slow push
and karaoke captions highlighting the key phrase in terracotta. Structurally it is
the format that competes.

**But it must not ship on today's pictures.** The frame I pulled shows roughly
eighteen pairs of boots strewn across a floor with the caption *"Two pairs per
person on the rack"* burned over it. There is no rack. At zone-page scale a
mediocre hero is a soft error; **at full-bleed video scale it is a flat
contradiction of the instruction printed on top of it.** And the 4:3 source
cannot fill 9:16, so it sits inside a blurred letterbox at both ends.

**The recommendation, in order:**

1. **Now, unblocked:** build photo-led verticals only for zones whose hero
   *passes the accept test*, including the new `contradicts` check. That is an
   honest subset, it is free, and it gives real performance evidence on the format
   before spending anything.
2. **Behind the click:** regenerate heroes as composed 9:16 frames (section 5),
   then rebuild all 114.
3. **Keep the typographic 16:9 for YouTube long-form and retire it for vertical.**
   Two formats serving two jobs, rather than one format serving neither. The 16:9
   film is a followable instructional document; the vertical is a hook.

**Thumbnails follow the same logic and the same expired premise.**
`ops/build_thumbnails.py` states as a design rule: *"Real contrast, no photograph
behind the type. There is no per-zone photography."* The 114 that exist are
typographically clean, on-brand, and completely imageless, at the 168 px they
are actually seen, a cream card with black type next to competitors' real
before-and-after photographs will lose. **Thumbnail click-through is the single
largest lever on the entire video stream**, and it is currently designed around a
constraint that stopped being true. Fold it into tier 3: the same regenerated hero
serves the page, the card, the vertical film and the thumbnail, at no extra
generation cost.

---

## 8. What "improvement" means for the narrated videos specifically

Everything here is unblocked. Ordered by how much it changes the outcome.

**1. Make the description work.** 7 of 12 published films link to a 404, and 113
of 114 contain a sentence that stops mid-word. This is not polish, the link is
the only path from a view to the site, and GOALS.md names arrivals as the
constraint. See A6 and A7. **Nothing about video quality matters more than this.**

**2. Fix the hook.** The first three seconds are a static title slide with 40%
dead space, with narration beginning over it. Open instead on the *standard*, the
one sentence from `done_looks_like` that tells a viewer what they will have at the
end: and, once tier 3 lands, on the picture of it. Same words, already written,
reordered.

**3. Put the picture in.** Median 126 seconds of text slides is the format's core
weakness, not its typography. Same change as section 7, same dependency.

**4. Fix the orphaned "Keys" chip.** A11. In all 114, both orientations.

**5. Fix the caption cue boundaries.** The SRT files are technically excellent,
maximum 84 characters, cue durations 1.9 to 7.6 s, every video has one, all within
the two-lines-of-42 guideline. But cue 1 merges the room, the zone name and the
first half of the opening sentence, then splits it across cue 2: *"Dining Room
Beverage or Coffee Station / Make a drink and hand it over without"* → *"crossing
into the kitchen."* Cues are timed to slides; they should be timed to narration
phrases. Numbered list items also lose their punctuation, so "1." renders as "1".
Half a day, and it improves accessibility and YouTube's transcript-based ranking
at the same time.

**6. Hit -14 LUFS.** A12. One decibel, thirty minutes, applies on the next render.

**7. Bitrate.** Measured across all 456 files: 1920x1080 at 30 fps with a **median
video bitrate of 141 kbps**, range 101-207. YouTube's own recommendation for
1080p30 is 8,000 kbps. On flat cream slides this is nearly invisible, which is why
nobody has noticed; the instant a photograph fills the frame it will be very
visible as blocking in the shadows and mush on the slow push. **Raise this in the
same render that adds the pictures, not before**, on today's content it would only
add megabytes. Target 8-12 Mbps for 1080p, and either treat the media plan's
3840x2160 master line as aspirational or correct the plan to say 1080p.

**8. Say the accessibility part out loud.** The six-S progress spine encodes
progress in colour alone. The pass name is written beneath it so the meaning is
recoverable, but the plan's own rule is that no information is carried by colour
alone, and adding a tick or a fill fraction to the completed segments costs
nothing.

**What I deliberately do not recommend:** re-recording narration. The neural voice
is consistent, loudness is consistent to within 0.2 LU across a ten-file sample,
and the script is drawn from the same corpus as the page. Narration is the
healthiest part of this pipeline.

---

## 9. The critical path, and where the click actually sits

```
A10 style source into repo ─┐
A4  build accept test ──────┼─► A5 run it over all 346 existing images
A1  fix 27 numeric claims ──┘                 │
                                              ▼
                          the list of what genuinely needs regenerating
                                              │
                                              ▼
                             ┌──────  BILLING CLICK  ──────┐
                             ▼                             ▼
                   tier 1: 89 card heroes        tier 2: 11 room bases
                             │                             │
                             ▼                             ▼
                 render pipeline B, retire A      SVG zone-map overlay
                             │                             │
                             └──────────► tier 3 ◄─────────┘
                                    re-shoot what failed A5
                                              │
                                              ▼
                           rebuild 114 videos + 114 thumbnails
```

**The click is not the first thing on the critical path. It is nearly the last.**
Everything above it is free, and every item above it is something that, if
skipped, causes generated images to be redone:

- Without **A10**, an overnight batch can drift into a second visual identity.
- Without **A4/A5**, we would pay to regenerate images that were fine and keep
  ones that are not, and we would have no way to stop a new keyless key station
  from passing again.
- Without **A1**, the good pipeline would print 27 fabricated statistics in crisp
  type, which is a worse trust position than the blurry ones we have now.

Sequenced this way, the click is followed by a batch that runs unattended,
self-retries what fails, and hands a human only the question a human is good at.

---

## 10. What I did not check

Stated as loudly as what I did, per CLAUDE.md section 0.4.

- **I opened 12 of the 144 shipped card faces.** The garbled bands on EM-005 and
  EM-006, and the statistics on EM-001, EM-005 and EH-004, are confirmed by
  opening those files. The brief's counts of "two garbled" and "eight with
  statistics" are neither confirmed nor refuted. A5 settles it.
- **I did not find the fake QR block in the current shipped set.** The review that
  reported it was written against a different, older 35-image set. Absent from my
  twelve is not absent from all 144.
- **I did not re-fetch Google's image prices.** The figures in section 5 come from
  `ops/generate_card_art.py`, recorded there as fetched 2026-09-04.
- **I could not run the exact CLIP token count.** The tokenizer download timed out
  twice. The token figures are a whitespace-and-punctuation proxy, which typically
  undercounts by 15-25%, so a handful of prompts may sit just over 77.
- **I checked the live site for two things only:** that the deck gallery returns
  200, and that EM-001's back is byte-identical between production and the
  repository. I did not verify the rest of the estate against production.
- **I did not open all 114 videos.** Format statistics come from ffprobe across all
  456 files; loudness from a ten-file sample; visual assessment from frames pulled
  at 3, 20, 60 and 110 s of one narrated film in both orientations, plus one
  photo-led vertical.
- **I ran three vision-model calls, not a study.** Three correct discriminations,
  one of which surfaced a permissiveness failure mode I have designed around. That
  is enough to prove the mechanism and not enough to characterise its error rate.
  A5 produces the characterisation.
- **SDXL-Turbo (6.5 GB) is already cached in `build/models/`** while
  `ops/image_local.py` is hardcoded to SD 1.5. I did not test whether it fits the
  8 GB RTX 2070 SUPER, and the existing comment records a measurement that full
  SDXL at 1024x768 peaks at 9.0 GB and spills, which is why 1.5 was chosen. Turbo
  at 512 would fit and is a materially better model, so there is a free local
  improvement here worth an hour of investigation. **I am not proposing it as a
  substitute for the click:** composing a five-object scene locally is the
  problem, and a better local model narrows that gap rather than closing it.
