# Product backlog, September to December 2026

Written 2026-08-24. Supersedes the queue content in `BACKLOG.md`, which is a
process document describing states and schemas rather than a list of work.

**How to read this.** Ordered by the sequence work actually has to happen in, not
by how appealing it is. Every item has an acceptance criterion that can be
checked by running something or fetching something, because "done" is otherwise
an opinion. Estimates are in operator sessions, where a session is a few hours
of focused work, and they are guesses.

**The rule that orders everything below:** nothing that improves conversion
matters until something can be measured, and nothing that adds product matters
until a stranger has bought something. So measurement comes first, then traffic,
then conversion, then product.

---

## EPIC 1: See what is happening (blocks everything)

Four experiments are designed, instrumented, and completely unreadable. This is
the only epic where every item is cheap and every item is blocking.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 1.1 | **Umami read access** | `ops/` can fetch visitor counts without a browser login | 0.2 | **Phil**, 3 clicks. **Partly done 2026-09-02: see note below** |
| 1.2 | Wire the share URL or API key into the dashboard | `python ops/dashboard.py` prints real visitors, not "not measured" | 0.5 | operator, still blocked on the share URL/key itself |
| 1.3 | Answer EXP-001: has a stranger ever clicked a buy button | a number in `ops/experiments.json`, `observed_daily_visitors` no longer null | 0.5 | operator |
| 1.4 | Answer EXP-002: does anyone reach the offer at the bottom of a zone page | scroll depth distribution recorded for 30 days | 0.3 | operator |
| 1.5 | Search Console: first impression data | 30 days of impressions exported and read | 0.5 | operator |
| 1.6 | ~~Wire measure.js and PWA icons into the 134 room and zone pages (issue #28)~~ | `ops/wire_measure.py`/`wire_pwa.py` report 0 skipped for `site/rooms/` and `site/zones/`, verified in a headless browser | 0.3 | **done 2026-08-29** |

**1.1 is the single highest value item in this document.** Everything in epics 3
and 4 is guesswork until it lands.

**1.1, corrected 2026-09-02.** The Umami API token is expired (401 on every
route) and no operator sandbox can read it programmatically, but that is not
the same as "unreadable": Phil read the analytics database directly on
2026-09-02 and recorded a real baseline in `GOALS.md` (47 sessions/30 days,
21/7 days, 1 organic from Bing, 0 from Google). This is a one-time manual
pull, not a live feed, so it will go stale the same way any hand-transcribed
number does; `STATUS.md` section 9 carries the same figures with the same
caveat. What is still genuinely blocked is 1.2: a share URL or API key so an
operator session can pull this itself instead of waiting on Phil to
re-transcribe it by hand each time.

**1.6 done 2026-08-29.** Chained `wire_measure.py` and `wire_pwa.py` into
`ops/build_zone_pages.py`'s own `main()`, right after the existing
chapter-SVG re-import, rather than running them as a one-off: this
generator's `<head>`/`<body>` templates never carried either block, so a
plain rewrite of any of the 134 pages would have re-deleted them the next
time anyone touched zone or room content, the same trap issue #26 already
names twice. Verified: all 134 pages carry `MEASURE:BEGIN` and `PWA:BEGIN`
with 0 skipped; a second full rebuild produced a byte-identical diff
(proves the chaining is idempotent, not a lucky one-time state); a headless
Chromium check on a sample room, zone and both deck-gallery pages confirmed
`measure.js` is actually requested and the favicon/apple-touch-icon paths
resolve 200. Two deck-gallery pages picked up the same missing blocks as a
side effect (they carry the analytics tag but never had either marker) and
are now wired too, same defect, not scope creep. Full detail on issue #28,
closed.

---

## EPIC 2: Fix what is broken or dishonest

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 2.1 | **Listmonk sending identity** (issue #15) | a 6S signup receives mail branded 6S Success, not Compassion Benchmark | 1.0 | Phil decides, operator builds |
| 2.2 | Restore the signup form | `python ops/wire_signup.py` re-run, form live on 6 pages | 0.2 | **blocked on 2.1** |
| 2.3 | ~~Sitemap lastmod stamps every URL with today (issue #23)~~ | `sitemap.xml` shows real per-page modification dates | 0.5 | **done 2026-08-24** |
| 2.4 | ~~Chapter 39 promises printables that do not exist (issue #19)~~ | either the printables exist or the promise is removed | 1.0 | **folded into 2.7, 2026-08-29** |
| 2.5 | Chapter 47 plates are monochrome (issue #18) | Phil decides regenerate or accept | 0.2 | **Phil** |
| 2.6 | ~~Kitchen safety pass never mentions gas (issue #16)~~ | gas hazard present in the Kitchen zone data, or a recorded reason it is not | 0.5 | **done 2026-08-25** |
| 2.7 | **One image generation route** (issues #1, #2, #18, #19, #20) | any route that produces a usable image without Phil pasting prompts by hand | 2.0 | **one decision, not five** |
| 2.8 | **Stripe business website field still reads Ledgerium** (issue #21) | receipt and dispute-review business website reads 6s-success.com, not ledgerium.ai | 0.1 | **Phil**, blocked by a Stripe safety check on live payment accounts |
| 2.9 | ~~Revenue outage: all 6 live payment links deactivated in Stripe~~ | `ops/check_live_links.py` checks the live pages against Stripe's active flag and preflight reports it | 1.0 | **done 2026-08-30, Phil** |
| 2.10 | ~~Restoring a Quest backup could silently erase real progress~~ | a corrupted or hand-edited backup entry cannot turn an already-done card back to undone, on the live site or in the app | 0.3 | **done 2026-09-03, operator** |

**2.10, found 2026-09-03, this operator, by checking the merge comment's own claim instead of trusting it.** Both restore paths (`site/assets/js/quest.js`'s `restore()`, the live customer-facing one, and the mobile app's `lib/importProgress.js`) merged an incoming card's timestamp with `(a && b) ? Math.min(a, b) : (a || b)` and never checked either side was a real number. A backup file with one non-numeric, zero or negative value for a card still passes `JSON.parse`; `Math.min` on a non-numeric value returns `NaN`, which `JSON.stringify` writes as `null` and the app's own `done[cardId]` checks read as falsy, silently marking a finished card undone. Reproduced live against the served `quest.html` with a real headless-browser file-input restore before writing the fix (script proved the bug, then proved the fix), not assumed from reading the code. Fixed both files to drop any non-finite, non-positive value before merging. Added three regression tests to `mobile/quest-app/lib/importProgress.test.js` (all pass; `npm test` 27/27, was 24). New `gate_quest_restore_validates_timestamps` in `ops/preflight.py` for the web side, which has no JS test harness in this repo; proved it fails on a planted regression (the guard removed) and passes restored. Also found and fixed the reason nothing would have caught this either way if it were a mobile-only regression: `mobile/quest-app/**` was in no CI workflow's path filter at all, so a change there got zero automated signal, the same shape `checks.yml`'s own header comment names for `ops/`. New `.github/workflows/mobile-checks.yml` runs `npm test` (plain node, no install needed, confirmed by running it with `node_modules` moved aside) on every push touching `mobile/quest-app/lib/**`.

**2.9, found and fixed 2026-08-30 by Phil, eight parallel specialist audits
converging on the same answer four independent ways.** A deactivated Stripe
Payment Link still returns HTTP 200 and serves the same JavaScript shell as
a working one, resolving to "no longer active" only once a browser runs it,
so every repository-level check (`check_sellable.py` included) stayed green
while every buy button on the live site was dead for at least three days.
Fixed with `ops/check_live_links.py`, which asks Stripe's API about the
links the live site actually serves rather than the repository. Same pass
also corrected copy that would have shipped alongside it as new public
falsehoods (terms.html claimed 6 items for sale against a real 155; every
surface promised delivery "within the hour" against a measured 85-minute
median and 12.4-hour longest gap; privacy.html's only mention of payments
was a promise to update the page before they went live, which happened
weeks earlier) and hardened the deploy path (`nginx -t` now runs in CI
before publish; three proxied locations got fail-fast timeouts). Full
account in `RETRO-2026-08-30-cycle6.md`. The code fix is on `main` and
built by CI (confirmed by this operator, run green against `8413b9a`);
whether the redeployed live site is actually taking money again is
unconfirmed from this sandbox (no egress to 6s-success.com or the Stripe
API) and needs a session with real access to close the loop.

**2.7 correction, 2026-08-30, this operator.** Two commits this same morning
(`4d9401a`, `79b5133`) fixed the pixel-level trademark and "Set in Order"
defects behind issue #1 and closed it out in a GitHub comment as resolved.
Verified by opening the served files directly rather than trusting the
comment: both were still live. The fix landed in a different, newer
rendering path (`ops/build_card_template.py`, writing to the gitignored,
unshipped `build/card-fronts/`) than the one the free public gallery
actually reads (`ops/split_deck_cards.py` into `site/assets/cards/`),
and nothing had wired the two together. Mitigated in `d0d95de`: both codes
withheld from the live gallery via a new `BRAND_EXCLUDE`, `index.json` now
honestly says 88 of 90, and a new preflight gate
(`gate_deck_art_withheld`) fails if either reappears live by any route.
This is withholding, not the fix; issue #1 stays open. The underlying gap
this exposes: **the deck now has two separate, unconnected art pipelines**
(the scanned-sheet one `split_deck_cards.py` owns, and the new hero+template
one `build_card_template.py` owns), and closing a defect in one silently
leaves it live in the other. Worth a real decision, not an operator
guess: which pipeline is the live gallery's long-term source, or does
`split_deck_cards.py` need to start reading `build_card_template.py`'s
output. Not resolved here.

**2.7 route established 2026-08-28, by Phil directly (commits `3341c0a`,
`e6a3e5f`), not by this operator.** The route is Phil generating each image
himself against a self-contained prompt, dropping the file in
`Desktop/6S-Generated-Images`, and running `ops/import_generated_art.py
--apply`, which checks card code, aspect ratio, size, flatness and a banded
top/bottom edge (a proxy for baked-in text) before it ships, then routes the
file to the right deck, splits front from back, rebuilds the gallery and
re-fingerprints. Tested end to end with four synthetic files (one accepted,
three correctly refused with reasons) before the synthetic test image was
removed again. `build/prompts/ALL-PROMPTS.md` holds the 92 outstanding
prompts: the 4 entryway cards flagged for replacement (2 carry a visible
Amazon-style brand, closing issues #1/#2's root cause) and the 88 mudroom
cards with no art yet. This does not close #1, #2, #18 or #20: the route
exists, but the images themselves still have to be generated by Phil one at
a time, and only 2 of 90 mudroom cards (MM-001, MR-001) are illustrated so
far, per the gallery's own honest count. Still correctly "blocked-on-art"
until he generates the rest; not
operator-actionable, since this sandbox has no image-generation path
(no GPU, no API key, confirmed again every cycle this is checked).

**Also new 2026-08-28, worth flagging rather than acting on:** the mudroom
deck (90 cards, spec extracted to `build/mudroom-cards.json`,
`site/deck-gallery-mudroom.html` live but unlinked from anywhere else on the
site) is a second illustrated deck, which `ROADMAP-2026-2029.md` section 4
and this file's "deliberately not in this backlog" section both name as
something to hold until the free Entryway deck has produced evidence, which
it has not yet. This is Phil's own explicit, direct action, not a drift this
operator caused or should second-guess; recorded here so the roadmap and
this backlog stay honest about it rather than silently going stale. The
gallery page is correctly unlinked and states its own incompleteness (2 of
90 illustrated) rather than being presented as a finished product.

**2.7 replaced five separate items.** Card trademarks, stale card art, the
monochrome chapter, the QR plates and the deck families are the same blocker
under five titles: every one needs images regenerated and nothing else about any
of them is undecided. There is no local path, the VPS has no GPU and torch here
is CPU only, so this is about establishing a route rather than five calls from
Phil. Verified 2026-08-25 that none of the five has anything false live.

**2.4 closed as a separate row, 2026-08-29.** Re-verified rather than trusting
the 2026-08-25 comment on issue #19: the only chapter 39 plates the live site
serves are `ch39-image01/02/04.jpg`, on `site/rooms/kids-bedroom.html`, and
none of their alt text or surrounding copy mentions a QR code or a printable.
No page anywhere on the site promises a chapter 39 printable that does not
exist. Issue #19 closed as folded into 2.7, the same shared image-route
blocker as the other four.

2.1 is a real blocker with a real cost: the list is the only asset that
compounds, and six of seven prospects have already been lost with no way to
reach them.

**2.2 marked blocked on 2.1, 2026-08-29.** Read `ops/wire_signup.py` and issue
#15 before treating this as pickable: the form was deliberately reverted
because the shared Listmonk sends confirmation mail as "Compassion Benchmark"
with a dead `localhost` opt-in link, so restoring it now recreates the exact
defect it was pulled for. Not actionable until #15 is decided.

---

## EPIC 3: Traffic (the constraint, and it is slow)

Nova has no list. Search is the only durable route and it takes 12 to 18 months.
Everything here is planting, not harvesting.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 3.1 | Publish the ten LinkedIn posts | posted, and referral traffic visible in analytics | 0.2 | **Phil** |
| 3.2 | Daily LinkedIn drafts keep running | already automated, 8am Denver | done | automated |
| 3.3 | The six tier-0 photographs | 6 files in `content/images/intake/`, wired into 3 zone pages | 1.0 | **Phil** generates, operator wires |
| 3.3b | ~~Import the unused chapter SVG figures~~ (was: import from the 1,000 images; see correction below) | 2 imported and gated; the other 34 read individually before any of them ship | 3.0 | **done 2026-08-27** |

**3.3b was written on a false premise and is corrected here, same day.**

What I wrote this morning: the site uses 41 of about a thousand images that
exist, so the image programme is an import problem rather than a generation
problem. The audit that followed showed the opposite, and the correction
matters more than the import did.

The 41 in use are not a sample of a thousand good ones. They are the survivors
of an editorial QA pass that ran chapter by chapter and is recorded on disk in
35 files named `CHxx_IMAGE_FINALIZATION_NOTES.md`, sitting next to the images
themselves. The rejections have causes, written down: fake QR codes advertising
printables that do not exist, baked in em dashes, trademarked packaging,
invented taxonomies, and claims that contradict the book. Ch33's pantry batch
lost 9 of 20 plates to trademarks. Ch36 lost 16 of 20 to fake QR codes.
Importing the rest is not filling a gap, it is reversing a careful decision.

Three further findings, each of which closes a route I had counted on:

* **The 94 shop photographs cannot go on the site.** They are a sheet metal
  fabrication floor, not a home: forklifts, dip tanks, flammable storage. One
  frame has an unobscured human face beside a McKinstry Co. sticker; another
  shows an Alaskan Copper and Brass bin. That is a real, identifiable client
  and a real, identifiable person, and no consent for public web use exists.
  **RED band. Not to be published without written permission from both.**
* ~~All 90 Entryway deck images are the wrong artefact.~~ **Wrong, reversed
  2026-08-27.** This call read the cards as failed editorial photography and
  rejected them on that basis. Phil corrected it: the chrome is the product,
  these are game cards, and the two panel mockup is the front and back face
  of a real 90 card deck with a working taxonomy. `ops/split_deck_cards.py`
  splits every sheet into front and back faces and `ops/build_deck_gallery.py`
  now ships all 90 on `deck-gallery.html`, filterable and flippable. See
  epic 5 note under 5.1 for the sales-model question this reopens.
* **Chapters 40 to 50 have zero images, not zero clean ones.** Verified by
  count. The eleven rooms with no coverage cannot be fixed by sourcing at all.

What actually was unused: **36 hand authored SVG figures inside the chapter
HTML for chapters 31 to 39**, vector rather than generated raster, already in
the site palette and font stack, none of them anywhere on the live site.

**Finished 2026-08-27.** All 36 read individually, per the whole lesson
above. Six are now imported and gated by `ops/import_chapter_svgs.py`: the
original two (Washing Toys, Lift the Dry Mess), plus four more this cycle
(landing spot cleaning sequence, toaster lift-and-empty, burner soak-first,
sofa deep cleaning), each an unambiguous single-zone technique diagram the
same way the first two were. The other 30 are room-wide zone maps, kit
lists and before/after pairs: the import mechanism wires one figure into
one zone page's Shine section, and a room-wide figure has no single zone
to belong to without misattributing content to a page that never claimed
it. Left out on purpose, not for lack of reading them.

The chapter source itself turned out to be reachable in this repo the
whole time, at `content/book/6S-Success-Chapter-*/chapter_*_final.html`,
committed 2026-08-25. `import_chapter_svgs.py`'s `BOOK` constant pointed
only at Phil's Desktop and its "no final HTML for chapter 36" error was
taken at face value by two prior cycles, neither of which checked whether
the file existed somewhere else in the repo. It did. The script now tries
the repo path first, Desktop second. This does not change the note below:
the 864 book plates, 90 deck illustrations and 94 photographs are a
different, larger asset set that really is Desktop-only, confirmed again
this cycle by checking `content/images/` here still holds only 3 files.

This does not remove 3.3. Six matched before and after pairs of a real house
are still the strongest proof the site could carry, and no library has them.
The library was never going to substitute for them.

**Checked 2026-08-26, same day this was written: not reachable from the
operator sandbox.** Searched this environment's whole filesystem for the 864
book plates, 90 deck illustrations and 94 photographs described above as
"outside the repository." None of them are anywhere in this container either;
`content/images/` here holds 3 files, a prompts folder. "Outside the
repository" evidently means outside this sandbox too, most likely on Phil's
own machine or a drive this operator has never had access to. This is the
same shape of blocker as Umami and Stripe: real, unblocked-looking work on
paper that is actually waiting on access only Phil holds. Needs either the
images placed somewhere this environment can reach (a repo path, even
gitignored) or a session with that access doing the import directly.

**Both notes are true and they explain each other.** The correction above was
written from a session running on Phil's own machine, where the images are;
the access note below it was written by the nightly cloud routine, where they
are not. Anything touching this library has to run locally. That is now
recorded in `ops/import_chapter_svgs.py`, which reads from Phil's Desktop and
will simply report a missing folder anywhere else rather than pretend.

**New 2026-08-30, entirely by Phil's own commits, same shape as the note
above.** `ops/generate_zone_heroes.py` generates a hero photograph for each
of the 114 zone pages, built from that zone's own `done_looks_like`
sentence, and `ops/wire_zone_heroes.py` is already chained into
`build_zone_pages.py` per this file's own generator-ownership rule. The
engine moved from SDXL Turbo to SD 1.5 after measuring 33x faster and no
VRAM spill on his 8GB card; 83 of 114 heroes are generated on his machine
so far, 70 already matched to a page. Not operator-actionable in this
sandbox: `ops/wire_zone_heroes.py --check` shows 0 heroes reachable
(`build/heroes/zones/` empty here), the same Desktop-only wall as the 1,000
existing images above. The same commit also shipped `site/kit.html`, the
eight product types every micro zone asks for, in method order, on
purpose not linked from the 114 zone pages so it does not divert the
higher-margin print-pack click. It was live but missing from
`sitemap.xml`; fixed 2026-08-30 by re-running `ops/build_seo.py`, which
owns that file, and a new `preflight.py` gate now fails on this class of
defect on its own.
| 3.4 | Measure whether images change anything | before/after comparison on those 3 pages after 30 days | 0.3 | operator, needs 1.1 |
| 3.5 | Second wave of images if 3.4 is positive | 30 more images live | 3.0 | conditional on 3.4 |
| 3.6 | ~~Internal link depth audit~~ | every zone page reachable in 3 clicks from home | 0.5 | **done 2026-08-24** |
| 3.7 | Article expansion, only on measured queries | new articles written against real Search Console queries, never invented ones | 2.0 | needs 1.5 |
| 3.8 | Directory and citation listings, only legitimate ones | listed where a real human would look for this | 1.0 | operator, see note |
| 3.9 | ~~Seven orphaned root-cause articles wired into the link graph~~ | every article reachable from a relevant zone page, not just the articles index | 0.3 | **done 2026-09-01, operator** |
| 3.10 | Post the 114 zone-reset videos to a social video platform | at least one clip live on YouTube Shorts, TikTok or Instagram Reels, referral traffic checked once 1.1 lands | 0.2 | **5 narrated videos live 2026-09-02/03, Phil.** 109 to go, same wall, no operator credential |
| 3.11 | ~~Pinterest and Instagram save-and-share cards, prepared~~ | 114 zones, both surfaces, correct dimensions, verified by opening the rendered images | 0.4 | **done 2026-09-02, operator** |

**3.7 is deliberately blocked on 1.5.** Writing articles against guessed queries
is how a content site accumulates pages nobody searches for.

**3.11 done 2026-09-02, this operator, from GOALS.md's own list of what needs
no account to prepare.** GOALS.md O1 names two things buildable under the
traffic constraint without Phil: SEO (checked this cycle, technically clean:
homepage is `index, follow`, canonical is correct, sitemap and robots.txt
have no crawl block, so the zero-Google-visits fact is a new-domain
compounding problem, not a bug, matching `ROADMAP-2026-2029.md`'s own 12 to
18 month estimate) and the Pinterest/Instagram crops, which did not exist
yet. Built `ops/build_social_pins.py`: a static "save this" checklist card
per zone, one for Pinterest (2:3, 1000x1500) and one for Instagram feed
(4:5, 1080x1350), composed fresh from `content.json` rather than cropped
from the existing 9:16 video, per `MEDIA-OPERATIONS-PLAN.md` section 5's own
rule against auto-cropping a frame composed for a different aspect ratio.
Fully typographic, same reasoning `video_zone.py` already gives for needing
no Desktop source or photo library: 109 of 114 zones have no photograph
either way. Found and fixed two real defects before shipping, both by
opening the actual rendered PNGs rather than trusting a clean exit code
and the right byte dimensions, the same discipline cycle 8's book-cover
near-miss named: a flexbox `flex:1` list doesn't shrink below its own
content height, so it silently pushed the footer past the canvas edge on
every card; and `line-height:1` on the brand-font footer text overflowed
its nominal line box enough to clip descenders on the shorter 4:5 canvas
specifically, invisible on the taller 2:3 one at the same relative margin.
Fixed both, re-verified on the original zone plus the two real content
extremes (longest zone name, longest purpose sentence) before batch
building. All 114 zones, both surfaces, 28 MB total, dimensions verified
by reading the PNG header directly (no new dependency; `ops/requirements.txt`
deliberately stays pymupdf-only, per 6.40's own reasoning). Wired into
`ops/dashboard.py` (`social_pin_line()`) the same way `zone_video_line()`
and `zone_photo_video_line()` already surface the other two video formats,
so this does not become the next cycle's hidden-finished-work find; new
`gate_dashboard_social_pins_live` in `preflight.py`, proved to fail in an
isolated worktree before trusting it. Does not post anywhere: that needs
the same account only Phil can create as 3.10, unblocked the moment it
exists.

**3.10 first video live 2026-09-02, Phil directly, commit `e79b843f`.**
`youtu.be/ItVRfZMGoJo`, the Landing Zone clip, uploaded to a real YouTube
channel with a real title and description. This is the 16:9 cut
(`build/video/zones-16x9/`, 6.43), not a vertical Short; the acceptance
line's "YouTube Shorts" is not literally met, "at least one clip live on
YouTube" is. Uploading this one first, rather than all 114 at once, found
two real defects that would otherwise have shipped everywhere: all 114
titles used the British "organise" against a site that uses the American
spelling 1,276 times to 237 and a US audience whose search volume favours
it, and 13 of 114 descriptions linked to a reconstructed zone-page slug
that did not match `build_zone_pages.py`'s own `NAME_MAP` output, a real
404 (the Landing Zone's own page is `entryway-the-landing-spot.html`, not
`entryway-the-landing-zone.html`). Both fixed at the source in
`ops/build_youtube_metadata.py`, which now imports `build_zone_pages` for
its own slugs instead of reconstructing them, and all 114 regenerated
descriptions resolve. `GOALS.md`'s O1 table and narrative corrected to
match (was still "0 of 228," found stale this cycle). Referral traffic
from this one video is not yet checked, and 113 uploads remain, same wall,
still needing Phil's own hand on each one; not closing this row.

**3.10 update, 2026-09-03, this operator.** Read Phil's own same-day commits
directly rather than trusting the standing "no commit from Phil since
e79b843f" line eleven prior cycles had each independently reconfirmed
today: `ops/render_all_narrated.py`, written and running since, renders
each zone's clip a third way with real synthesised voice (edge_tts) and
matching captions, replacing the silent cuts rather than adding to them.
17/114 zones built and committed under `build/video/zones-narrated/`
(verified by listing the directory, not assumed from the commit
messages), 5 of them (all Entryway zones) already posted live per commit
`42264b13`; the one earlier silent upload is now private. Two real gaps
followed from checking this against the tooling meant to track it rather
than stopping at "found it, noted it." First, the same hiding-finished-work
shape as every sibling video format below: nothing on the dashboard said
this one existed. Fixed with `narrated_video_line()` in `ops/dashboard.py`
and `gate_dashboard_narrated_videos_live` in `preflight.py`, proved to fail
on a real partial build and pass on a missing/empty one. Second, and more
consequential: `.github/workflows/hourly-brief.yml`'s own "Commit the
check-in record" step runs `git push origin HEAD:main` but the job
declared only `permissions: contents: read`. Its real logs (pulled via the
GitHub tools, not assumed from the green checkmark) show every push
failing with "Permission ... denied to github-actions[bot], 403" and
`continue-on-error: true` on both the check-in and commit steps swallowing
it silently; `git log --all --grep="Hourly check-in"` returns zero commits
across the workflow's entire history. `ops/state-checkin.json` and the
`youtube_published` figure `gate_goals_published_videos_current` (added
2026-09-02) checks `GOALS.md` against could therefore never have moved
past whatever a human committed by hand, no matter how many real
measurements the hourly job took on its real internet-connected runner.
Fixed the permission to `contents: write`; added a static
`gate_workflow_push_permissions` in `preflight.py` so any future
git-pushing workflow fails preflight on the same shape without needing
network or a token, proved to fail on a synthetic broken workflow and
pass on the real fixed one. Did not hand-edit `GOALS.md`'s gated "5 of
228" figure or `state-checkin.json`'s persisted count: this sandbox has
no YouTube egress to measure it directly (confirmed by running
`ops/checkin.py` here, which correctly reported it could not reach
YouTube), and writing an unverified number into a file another gate
trusts is exactly the defect this cycle just fixed one layer up. The next
scheduled hourly run should be the first in this workflow's history to
actually persist what it measures.

**3.10 found 2026-09-01, this operator, regenerating the command deck.**
`ops/dashboard.py`'s own "Video" line read "0/114 episodes shot" against a
scripted long-form episode tracker that genuinely has not started, the same
cycle a real commit (`a44335a`) ffprobe-verified 114 short vertical
zone-reset clips, 79 MB, already rendered by `ops/video_zone.py`. The
dashboard said nothing about that second product existing at all, the
copy-vs-control shape `CLAUDE.md` names, here hiding finished work rather
than overclaiming it. Fixed the dashboard with a second, distinct line
(`zone_video_line()`, matched by the exact slug the renderer builds
filenames from) and a new `gate_dashboard_zone_videos_live` in
`preflight.py`, proved to fail by reverting the line to the old string and
watching it fail naming both broken cases, then restored and reran clean.
Confirmed directly, not assumed: no site page links to `video/zones`
(grepped every served HTML file), so the clips are rendered but posted
nowhere. Filed here rather than fixed further: posting to a social video
platform needs an account only Phil holds, full detail in
`OWNER-ACTIONS.md` item 11.

**3.8 was researched and deliberately not executed, 2026-08-24.** No verified
physical location exists for local directories, generic submission lists skew
toward low-quality link schemes, and actual submission means creating accounts
under the business's identity on third-party sites, which is worth Phil's
awareness first. Full reasoning in `GROWTH-PLAYBOOK.md` section 4. Revisit if a
specific, clearly legitimate, niche-relevant directory is identified.

**3.9 done 2026-09-01, this operator, found running `ops/link_graph_report.py`
cold rather than trusting the last clean reading.** 7 of 29 articles had
exactly one inbound link (the articles index) against a sibling average of
82: real, written, on-topic content nobody could reach except by browsing the
index page directly. Read all seven rather than assuming why. Two named a
root cause `CLAUDE.md` section 6 lists that `ZONE_READING` (the list every
one of the 114 zone pages already carries) had never covered: poor
visibility (`why-you-cant-see-your-own-clutter`) and too many steps
(`why-you-have-to-dig-for-what-you-need`). Added the first; left the second
out on purpose, because this file's own comment above a different entry
already assigns "too many steps" to `family-wont-put-things-back`, and a
second article on the same named root cause would duplicate coverage rather
than fill a gap. The other five (`why-mail-piles-up-by-the-door`,
`why-you-always-lose-your-keys`, `how-to-organize-a-junk-drawer`,
`why-the-medicine-cabinet-never-gets-cleared-out`,
`why-you-cant-find-the-right-charger`) are not general root causes, each
already links out to one specific zone page and only makes sense there, so
a new `ZONE_SPECIFIC_READING` dict in `ops/build_zone_pages.py` links back
from exactly that one zone instead of all 114. Verified with
`link_graph_report.py` before and after: thin articles dropped from 7 to 1,
the one left has a documented reason. `check_urls.py` (184/184),
`audit_pages.py` (188 pages, 0 findings) and `preflight.py` all clean after.

**Found and fixed in the same pass, more consequential than the linking
itself: regenerating `build_zone_pages.py` in this sandbox silently
unpublished all 110 approved zone hero photographs.** `ops/wire_zone_heroes.py`'s
`approved()` re-hashes the source PNG in the gitignored, Phil-only
`build/heroes/zones/` before trusting a verdict, and this sandbox has never
had that folder. Every previous cycle avoided the defect only by never
running `build_zone_pages.py` end to end here; this is apparently the first
time in the project's history anyone has. Reproduced directly, not
theorized: hero count on disk went 110 to 0 in one run, `og:image` fell back
to the generic room-map picture on all of them, and `gate_image_coverage`'s
own no-source fallback (6.8) did not catch it, because it only checks the
wired count and the advertised count agree with each other, and a rebuild
that strips both together in lockstep passes that check clean. Fixed
`approved()` to trust the committed verdict by name when there is nothing
to re-hash, the same fallback shape 6.8 already used one layer up, and added
`ops/hero-fallback.json`, a committed record of the exact figure HTML for
all 110 already-approved zones extracted from the last known-good commit,
restored by a new `fallback_wire()` in `wire_zone_heroes.py` whenever no
source PNGs exist. New `gate_zone_heroes_stable` in `preflight.py`, checked
against the approved count from `hero-verdicts.json` rather than internal
self-consistency, the actual gap; proved it fails by removing the fallback
file, rerunning the generator, and watching hero count go 110 to 0 and the
gate go red, then restored and reran clean.

---

## EPIC 3B: Test local demand for the service SKUs (the gap in this backlog)

A strategy review on 2026-08-24 found a real hole: Epic 3 is entirely organic
search, and nothing anywhere tests demand for the two SKUs that already have
working Stripe links and are the only route to $20,000 that does not require a
mid-sized media property's worth of traffic. Seventeen In-Home Days is $20,400
a month at 3,900 visitors rather than 246,000.

The missing input is not a product. It is one demand signal that costs a few
hundred dollars and 90 days, rather than years of search compounding.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 3B.1 | **Approve a capped local demand test** | a budget and a stop date agreed in writing | 0.1 | **Phil**, this is a spending decision |
| 3B.2 | Google Business Profile for the service area | live, verified, linked from consulting.html | 0.5 | **blocked on Phil** |
| 3B.3 | Referral partner outreach: agents, senior move managers, organizers | 20 to 30 real contacts made, responses logged | 2.0 | **Phil** makes contact, operator drafts |
| 3B.4 | Run the test to its stop date | pass or fail recorded against G2 below, either way | 1.0 | operator |

**3B.1 is a financial commitment and therefore not mine to make.** CLAUDE.md
puts material spending in the RED band. The recommendation is a few hundred
dollars and a hard stop at 90 days, reported pass or fail, not left open ended.

**3B.2 checked 2026-08-29, not operator-actionable end to end, same wall as
3.8.** Grepped the live site and every operating document for a business
phone number before treating this row as pickable: none exists anywhere,
and a Google Business Profile for a service-area business needs one for
verification. Creating and verifying the listing also means opening an
account under Phil's identity on a third-party platform, the same category
of action `GROWTH-PLAYBOOK.md` section 4 already named for 3.8 and declined
to do without his awareness. Prepared everything short of that: business
name, category, a 480-character description drawn only from what
`consulting.html` already says, the exact seven-town service area copied
verbatim so the listing cannot disagree with the site, honest "by
appointment" hours instead of guessing fixed ones, and an explicit warning
against seeding reviews or a star rating before a single paid reset day has
happened. Full package at `build/gbp-listing-package.txt`. Needs a phone
number (a free Google Voice number is enough) and five minutes of his own
account before this can go live; not blocked on the 3B.1 budget decision,
since the listing itself costs nothing, only the paid test that might
follow it does.

**3B.3 drafted 2026-08-29, same shape as 3B.2: prepared everything short of
the outreach itself.** Nothing had been drafted before this cycle. Wrote a
message template for each of the three named partner categories (senior
move managers, real estate agents, professional organizers), grounded only
in what `consulting.html` and `site/about.html` already say publicly, plus
a response-tracking log matching the accept criterion's "responses logged."
None of the templates offer a referral fee or any other compensation on
purpose: paying agents for referrals can run into real estate licensing
rules, and it changes the relationship for move managers and organizers in
a way worth Phil's own decision, not an assumption. None of the templates
claim a customer count, a rating, or a result this business has not
produced. Full package and reasoning, including why professional
organizers need the most careful framing of the three, at
`build/referral-partner-outreach.txt`; the log template at
`build/referral-partner-outreach-log.csv`. Sending a message to a named
business or licensed professional under Phil's name is the same category
of externally-facing action already declined to do alone for 3B.2 and 3.8,
so making contact stays his step. This does not need the 3B.1 budget
decision either, since it costs nothing but time and produces its own
signal independent of any paid test.

---

## EPIC 4: Conversion (do not start before epic 1)

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 4.1 | EXP-003: free artifact first vs method first | powered sample reached or 6 weeks elapsed, result recorded either way | 1.0 | needs traffic |
| 4.2 | Offer placement, if EXP-002 shows nobody scrolls | offer moved, measured, kept or reverted | 0.5 | conditional |
| 4.3 | Post-purchase sequence | a buyer receives a second useful email, not a pitch | 1.0 | needs 2.1 |
| 4.4 | ~~Cart abandonment: there is no cart~~ | decide whether checkout sessions can be recovered at all | 0.3 | **decided 2026-08-29** |
| 4.5 | ~~Give Corporate Lean 6S a real page and a working buy path (`REVENUE-REVIEW-2026-09-04.md` 4.5)~~ | a real page exists, deliberately no invented price | 0.5 | **done 2026-09-03, Phil, commit `9e7b1cd1`** |
| 4.6 | ~~Reframe the consulting funnel to lead with services rather than digital (`REVENUE-REVIEW-2026-09-04.md` 4.2)~~ | 20 of 20 room pages route to a consult, `consulting.html` takes a payment with no JavaScript | 1.0 | **done 2026-09-03, Phil, commit `9e7b1cd1`** |
| 4.7 | A small recurring product (`REVENUE-REVIEW-2026-09-04.md` 4.4) | a subscription concept, price and delivery mechanism recorded in `DECISIONS.md` | 2.0 | **Phil**, new pricing model |

**4.4 decided 2026-08-29, see `DECISIONS.md` D-015.** Yes, in principle:
every product here sells through a Stripe Payment Link, and a Payment Link
creates an ordinary Checkout Session behind it that the same poll pattern
`ops/stripe_fulfil.py` already uses for fulfilment could check for a typed
email with no completed payment, no webhook needed. Not verified against a
live account (no Stripe key in this sandbox, `docs.stripe.com` blocked) and
deliberately not built yet: the recovery send needs a working brand-correct
mailer first, the same blocker as 2.1 and 4.3, and code with nothing safe to
send is not worth carrying unused.

**4.5, 4.6, 4.7 added 2026-09-04, this operator, from Phil's own
`REVENUE-REVIEW-2026-09-04.md` (committed 2026-09-03 22:12, read cold this
cycle rather than left as a standalone document nothing else points at).**
Two of its six proposals were already fully tracked elsewhere before this
cycle started: 4.1 (Amazon KDP/Etsy) restates `OWNER-ACTIONS.md` items on
seller accounts, and 4.3 (publish the videos) restates 3.10 and
`OWNER-ACTIONS.md` item 11, both already Phil-blocked on a credential this
sandbox does not hold. 4.6 in the review (repair Listmonk) restates
`OWNER-ACTIONS.md` item 7, diagnosed down to the exact SMTP credential
2026-09-03, also already Phil-blocked. Not re-added here, to avoid a second
copy of the same blocked item drifting from the first.

**4.5 and 4.6, corporate pricing and the services-first reframe, both
overtaken by Phil's own commit before this cycle's fix could push.** This
operator's first pass verified the review's "no price and no buy path"
claim against the live site (`shop.html` already had a "Request a quote"
card to a prefilled `mailto:`, the same stopgap `OWNER-ACTIONS.md` item 7
names) and, rather than invent a price, filed both as decisions in
`OWNER-ACTIONS.md` item 14 and GitHub issue #30, deliberately not building
4.6 because `ROADMAP-2026-2029.md`'s G2 gate holds services back pending
the still-unstarted `3B.1`. Rebasing this cycle's commit onto `origin/main`
found Phil had already answered both directly, concurrently, the same
evening: `site/corporate.html` (new, generated by a new
`ops/build_corporate.py`) gives Corporate Lean 6S a real page, a qualified
enquiry form, and Service/FAQPage schema whose Offers deliberately carry no
price, exactly the "explain what determines scope instead of inventing a
number" answer to 4.5; and 20 of 20 room pages now route to a consult with
`consulting.html` itself fixed to serve a working Stripe link in plain
HTML, which is the funnel move 4.6 was waiting on a decision for. That is
Phil overriding his own roadmap's G2 gate by direct action, which is his
call to make, not this operator's to second-guess after the fact. Owner
action item 14 removed as a duplicate ask; GitHub issue #30 updated.

**4.7, a subscription, is a new pricing model rather than a page edit** and
needs the same kind of decision as 4.5: what it is, what it costs, and how
it is fulfilled monthly with no recurring-delivery mechanism in the
codebase today. Recorded, not built.

---

## EPIC 5: Product (last, on purpose)

The catalogue is not short of products. It is short of visitors. Nothing here
starts before epic 1 answers whether the funnel works.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 5.1 | Decide how card decks get sold (issue #20) | a decision recorded in `DECISIONS.md` | 0.3 | **Phil** |

**5.1 has new context as of 2026-08-27.** All 90 Entryway cards, full resolution,
front and back, are now publicly browsable for free at `deck-gallery.html` (see
the 3.3b correction above). The Entryway deck was already the deliberately-free
evidence deck, so this does not change what is being given away, but a visitor
can now see the entire paid-tier art direction (the shared style bible any
future deck would use) without buying anything. Worth weighing when 5.1 is
decided, not blocking it.
| 5.2 | Quest: does anybody finish a second card (EXP-004) | retention number known | 0.3 | needs 1.1 |
| 5.6 | **Rebuild the Quest as the primary way into 6S** | a stranger finishes one zone in their first session | 4.0 (1.1 done 2026-08-27) | operator |

**5.6 is a promotion, not a feature.** The Quest is free, installable, offline
and holds the whole method. It is the only asset that can teach 6S by doing
rather than explaining, and it is the honest route to the 164 item catalogue:
somebody who has just finished their kitchen prep counter is the only person for
whom a nine dollar Kitchen Pack is obviously worth buying. It moves ahead of the
rest of epic 5 because everything else in that epic assumes somebody already
understands the method.

**First increment done 2026-08-26: the zone-to-card handoff.** All 114 zone
pages' "Or draw a card free" link used to point at the same bare
`quest.html`, which for a first-time visitor meant reading about one zone
and then being offered a random card from anywhere in the house, or having
to hand-pick their room and zone again from two dropdowns. `build()` and
`begin("zone", {room, zone})` already existed and were already used by the
resume feature, just never exposed as an entry point. Each zone page now
links to `quest.html?zone=<its own slug>`; `quest.js` reads that param on
load via a new `findZoneBySlug()` (matching the same `url` field the
generator already stamps on every zone) and drops the visitor straight into
that zone's own six-card run, in method order, skipping the start screen
entirely. A bogus or missing slug falls back to the normal start screen
rather than blanking the page. Verified against the served pages in a
headless browser, not just read: clicking the real link from the Beverage
or Coffee Station zone page lands on that zone's Sort card, not a random
one; a plain `quest.html` load and a bogus `?zone=` both still show the
start screen. This does not by itself prove "a stranger finishes one zone
in their first session," since that needs traffic and measurement (epic 1)
this environment does not have. It removes one concrete piece of friction
between reading a zone and acting on it, which is what was buildable
without Phil or a credential this cycle.

**Second increment done 2026-08-27: the room handoff, and a landmine found
in the first one.** The 20 room pages had the exact same defect as the
zone pages before yesterday's fix, still pointing at bare `quest.html`.
Fixed the same way: each room page now links to `quest.html?room=<its
slug>`, matched via a new `findRoomBySlug()` against the `slug` field
`quest-data.js` already carries on every room, and lands the visitor in
that room's own run (mode `"room"`, method order) instead of the general
start screen and its two dropdowns.

The landmine: fixing this required checking whether a generator owned the
room pages, per the retro's own new rule two cycles running. It does,
`ops/build_zone_pages.py`, and its `offer()` function (the zone-page
equivalent band) still read `href="../quest.html"` with no `?zone=`, even
though every deployed zone page has carried the query string since
yesterday. Yesterday's fix edited the 114 generated files directly rather
than the generator that owns them, exactly the anti-pattern
`RETRO-2026-08-26.md` names twice from two earlier incidents and writes a
rule to prevent. It had not yet regressed anything live, because nothing
had re-run the generator since. It would have on the next zone content
edit. Fixed `offer()` to build the same `?zone=<slug>` link from data the
function already has, so source and output now agree and a future
regeneration cannot silently undo it. Also cost two hand authored SVG
figures on two family room zone pages, briefly: `build_zone_pages.py`
rewrites all 114 zone pages from scratch and re-imports those figures via
`import_chapter_svgs.py` as its last step, which needs Phil's Desktop and
correctly no-ops with a warning outside it, so the regeneration silently
dropped them in this sandbox. Caught in the diff before committing;
restored both files from HEAD rather than committed with the gap and
fixed forward.

**Verified:** All four gates plus `audit_catalog.py` clean after the
rebuild and the re-fingerprint. Headless Chromium against the served
pages: `quest.html?room=kids-bedroom` opens straight to that room's Sort
card, "Kids Bedroom > Bed and Sleep Zone, 1 of 36"; a bogus `?room=` falls
back to the start screen; the existing `?zone=` deep link still works
unchanged. Diffed the full regeneration before committing: 114 zone pages
produced byte-identical content (confirming the generator now matches
what was already live), only the 20 room pages' CTA and the two touched
source files actually changed, and the two SVG figures are intact.

**Third increment done 2026-08-27: the rooms directory, and a generator
found to be missing content that was never its own.** `resources.html`,
the book's own companion page and the only place all 20 rooms are listed
with their kits, still sent "learn more" clicks to bare `quest.html` and
the general start screen, the same defect the room and zone pages had
before the first two increments. Added a per-room "Or draw a card free"
link to `quest.html?room=<slug>` in `ops/build_resources.py`, reusing the
`findRoomBySlug()` mechanism the first two increments already built.
Regenerating surfaced a real problem the retro's rule does not yet cover:
the committed page carried two Stripe commerce links and the signup
withdrawal notice that `build_resources.py`'s own template never
produced, so a plain rebuild would have silently deleted both. Folded
both into the generator rather than restoring them by hand. Filed
`issue #26` on this as a process pattern: three cycles running, a
generator's real output has carried content the generator itself does
not know about. Verified in a headless browser: the Kitchen link opens
`quest.html?room=kitchen` straight into that room's first Sort card; a
bogus `?room=` still falls back to the start screen. All four gates and
`audit_catalog.py` clean.

What is left in 5.6: the homepage header nav's top item ("Start a reset")
still points at `zones/`, a directory page, rather than the Quest
directly, and the hero's primary CTA points at `method.html`; both
already link to the Quest one click further in.

**Decided 2026-08-27, not reopened again without new evidence.** Read
`ops/wire_nav.py`'s own docstring: pointing "Start a reset" at `zones/`
rather than the Quest was a deliberate call from a UX review, not an
oversight several cycles failed to notice. Changing it now would be a
guess about click depth with zero traffic data to test it against, which
is exactly what `CLAUDE.md`'s Decision Memory section warns against
("do not repeatedly reopen settled decisions without new evidence") and
what the roadmap's own ordering rule blocks (epic 4, conversion, waits on
epic 1, measurement). Leave both links as they are. Revisit only after
1.1 lands and there is a real scroll or click-through number to act on,
not before.

The S-pass entry point has no natural per-page home to deep-link from the
way rooms and zones do, since no page on the site is organized around a
single S rather than a room or zone; revisit only if a real page for that
shows up, not by inventing one.
| 5.3 | Native app wrapper | only if 5.2 shows real retention | 3.0 | conditional |
| 5.4 | Workplace and professional edition | only if horizon 2 bet B is chosen | 5.0 | conditional, 2028 |
| 5.5 | Corporate Lean 6S: quote flow already works | verified 2026-08-23 | done | done |
| 5.7 | ~~Wire the 155-SKU product spine live~~ | every SKU has a live Stripe product, price and payment link, is listed in `window.CATALOG`, and `ops/audit_catalog.py` passes against the larger live set | 2.0 | **done 2026-08-27, Phil** |
| 5.8 | ~~The finished Entryway deck was not linked anywhere a customer could reach it~~ | `deck.html` describes the real 88-card deck and links a downloadable print-at-home PDF | 0.5 | **done 2026-08-30, operator** |
| 5.9 | ~~No zone page mentioned its own $4 pack, only the $19 whole house pack~~ | every zone page with a sellable pack names it beside the house pack, with a real Stripe link | 1.0 | **done 2026-08-30, Phil** |

**5.9 done 2026-08-30, Phil.** 109 micro zone packs existed, priced,
deliverable, each with a live Stripe link, and none of the 114 zone pages
mentioned its own; every page offered only the $19/684-card house pack, so
a reader told exactly what was wrong with their mail station was offered
twenty rooms of cards and nothing for the one they were standing in. Each
page now names its own pack ($4 for 6 cards) beside the house pack, SKU
derived the same way `ops/build_catalog.py` builds it rather than a second
stored list. Verified by this operator against the served files, not the
commit message: `grep -l "Just this zone" site/zones/*.html` matches 109 of
114 zone pages; the 5 without it are the Entryway zones, which have no
per-zone SKU (correct, not a gap).

**5.8 done 2026-08-30, this operator, picking up the open thread named in
`RETRO-2026-08-30-cycle5.md` ("the deck still is not linked anywhere a
customer can reach... preparing the download and the page copy is not
[deploy gated]. That is next").** Verified rather than trusted: `deck.html`
still described a 46-card, unillustrated, five-zone-six-pass deck at "a
simple line drawing today" with invented future pricing ($12 illustrated,
$29 boxed), none of which matched the actual live product. The real deck,
read from `site/assets/cards/entryway/index.json`, is 88 cards across
twelve micro zones and nine card types (Micro Zone 12, Problem 11, Tool 12,
Skill 12, Habit 12, Upgrade 12, Event 8, Win 8, Room 1), fully illustrated
front and back, confirmed by checking that all 88 have both front and back
image files on disk. Rewrote `deck.html`'s title, meta, JSON-LD, hero copy,
the "what's in it" section (now six real cards with real published art
instead of six fabricated mockup cards naming zones that no longer exist),
"how to play", and the status block, which now says illustration is done
rather than promising invented prices for a future edition nobody has
decided to sell (5.1 stays open, not preempted here). Copied the already
built `build/6S-Entryway-Deck-PrintAndPlay.pdf` (20 pages, verified with
PyMuPDF, US Letter, front and back sheets) to `site/downloads/`, linked it
from `deck.html`'s two CTAs, and pointed `ops/build_deck_gallery.py`'s own
print-and-play link at it too (that file is generator-owned; hand-editing
`deck-gallery.html` directly would have been overwritten). The old
`site/deck/entryway-print-and-play.html`, a hand-built 46-card mockup with
placeholder "illustration to place" SVGs, was still sitemapped and
reachable with nothing pointing anyone away from it; replaced its body with
a short honest notice and links to the real PDF and gallery rather than
leaving a stale indexed page describing a different product.

**Caught before committing:** the first pass at wiring the new PDF into
`ops/build_deck_gallery.py`'s shared template put the Entryway PDF link on
the Mudroom gallery page too, since both decks render from the same
function. A Mudroom visitor, honestly 2 of 90 cards in, would have been
told to go print an Entryway deck they never asked for. The regenerated
diff caught it before it was committed. Fixed by making the print-and-play
mention conditional on `deck == "entryway"`, and while in that function,
also fixed a real pre-existing bug it surfaced: the meta description
template hardcoded the word "Entryway" regardless of which deck was
building, so `deck-gallery-mudroom.html` described itself as the "6S
Success Entryway deck" in its own search snippet. Both now read correctly
per deck.

**New finding, not fixed here, worth a look alongside 2.7's open pipeline
question.** `build/entryway-cardtext.json` (the text corpus) and
`site/assets/cards/entryway/index.json` (what the gallery actually serves)
both total 88 cards but are not the same 88: the corpus has EE-001 and
EP-005 (both withheld from the live gallery per `gate_deck_art_withheld`,
issue #1) where the gallery instead has EP-006 and EP-010, which are not in
the corpus at all. Left alone rather than guessed at: this is the same
two-pipeline shape 2.7 already flags as needing a real decision, not an

**2026-08-30, this operator: the same numbering mismatch hid a second,
larger defect, issue #29.** Opened 25 of the 88 live cards directly rather
than trusting the corpus's own list of what it had fixed. 15 still carried
the retired name for the second S baked into their pixels (EM-004, EM-009,
EP-001, EP-002, EP-003, EP-006, EP-007, EP-008, EP-010, EP-011, EP-012,
ET-009, ET-010, ET-011, ET-012), two of them (EP-006, EP-010) the exact
orphan codes named above that the corpus's 2026-08-30 text fix could never
have reached. A sixteenth, EP-004, is worse: its file is labelled Backpack
Explosion and shows a second, uncredited render of the Wet Shoes scene
instead, no Backpack Explosion art exists anywhere live. The print-and-play
PDF is unaffected, checked directly by rendering two of its pages: it comes
from the newer, corpus-driven pipeline and says Straighten correctly.
Withheld all 16 the same way EE-001/EP-005 were, via a new `CANON_EXCLUDE`
in `ops/split_deck_cards.py` unioned into `WITHHOLD`; `gate_deck_art_withheld`
now checks the union and was proved to fail by reintroducing one code. The
live gallery drops from 88 to 72 shown; the Problem card type specifically
from 11 shown to 1. `deck.html`'s counts, spine and one example card image
(EP-001, now gone) are corrected to match. This is a real, visible shrink
to the free evidence deck, not a rounding change, which is why it is an
issue (#29) rather than a quiet fix.
operator call.

**5.7 done 2026-08-27, entirely by Phil, both halves.** Two direct commits
closed this without operator involvement: `b10a278` extended `SELLABLE`,
ran the live Stripe sync, wired `window.CATALOG`, and fixed four defects
found only by doing it (Stripe's 100-item pagination cap silently
deactivating the original 6 payment links, an O(n^2) sync timing out
before the site update, `find_by_sku` returning retired links, and a
rebuild dropping the carried-over buy link); `3e5248c` fixed
`ops/build_epub.py` reading a hardcoded `[AUTHOR NAME]` placeholder
instead of `ops/front-matter.json`, which had blocked Amazon KDP
submission. Re-verified this cycle: `ops/audit_catalog.py` passes clean
against 159 live SKUs (158 of 159 buyable, only Corporate Lean 6S still
has no buy path) and all four content gates are clean. No operator action
remains on this item.

---

## EPIC 5B: The Home Quest smartphone app

Added 2026-08-31 from `super prompts/6S-SUCCESS-HOME-QUEST-MOBILE-CLAUDE-CODE.md`,
nine staged prompts for iOS and Android.

**The ordering tension, stated rather than buried.** This document's rule is
that nothing which adds product matters until a stranger has bought something,
and no stranger has. By that rule a native app belongs behind epics 1 to 4. Phil
has asked for it to be prioritised, and both things can be true: prompts 1 to 3
cost little, need nobody's permission, and produce a runnable app that makes the
core loop testable on a real phone. Prompts 4 onward are a different order of
commitment and are gated below on things only he can do. The split is where the
priority argument actually resolves.

**What already exists and does not need rebuilding.** `quest-data.js` is 372 KB
of platform neutral JSON holding all 684 cards across 114 zones. The web Quest's
loop is functionally tested end to end. Node 24 and npm 11 are installed. The
canonical content pipeline prompt 3 asks for is a transform of a file that is
already the single source both products share.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 5B.1 | ~~Prompt 1: audit repository, live app and content against the mobile target~~ | a written audit naming every gap between the web Quest and the mobile product principles | 0.5 | **done 2026-08-31, operator** |
| 5B.2 | ~~Prompt 2: product target, UX architecture, migration contract~~ | the contract states what moves, what changes and what a web user keeps when they install | 0.5 | **done 2026-08-31, cloud operator** |
| 5B.3 | ~~Prompt 3: shared foundation and canonical content pipeline~~ | `npx expo start` runs, the app draws a real card from the shared corpus, and the corpus is generated from `quest-data.js` rather than copied by hand | 1.5 | **done 2026-08-31**, verified: 1,131 packages resolve, 539 modules bundle to 1.73 MB, Metro serves it over the LAN |
| 5B.4 | Core loop parity on device | draw, do, done, stop, resume and zone finish all work in Expo Go on a real phone, offline | 1 | **CLAIMED 2026-08-31 by the laptop operator.** Writing the numbered on-device script so Phil's five minutes produce facts. The scan itself remains his. |
| 5B.5 | Web to mobile import | a Quest backup file taken from the browser restores into the app with progress intact | 0.5 | operator, merge logic verified end to end against a real browser backup 2026-08-31, on-device picker still unverified |
| 5B.6 | Prompt 4: production iOS app | builds and installs from a development build | 2 | **blocked**, needs an Apple Developer account |
| 5B.7 | Prompt 5: production Android app | builds and installs on a device | 2 | **blocked**, needs Java installed locally or an Expo cloud build account |
| 5B.8 | Prompt 6: household, commerce and engagement | household progress is shared between two profiles | 3 | **blocked** on the accounts layer, same wall as 6S Plus |
| 5B.9 | Prompt 7: quality, privacy, security, accessibility | WCAG 2.2 AA checked on device, photographs proven never to leave it | 1 | **static half done 2026-08-31, laptop operator; one contrast defect corrected 2026-09-03.** Six controls given roles, labels and hints where they had none. Decorative colour hidden from assistive tech. Offline promise now enforced by a test that fails on any fetch. **On-device half still open**: announcement order, focus movement and gesture alternatives need a real screen reader. |
| 5B.10 | Prompt 8: store submission and launch | listings live | 2 | **blocked**, needs both store accounts |
| 5B.11 | Prompt 9: continuous target state and autonomous improvement | the app's own improvement loop runs | 1 | **second run done 2026-09-03, operator.** Recurring by the prompt's own design, not a one-time completion. Found and fixed a real WCAG contrast defect; see the note below. |

**5B.9 correction, 2026-09-03, this operator, Prompt 9's second cycle.** The
"12 contrast pairs measured and passing, weakest 3.04:1 against a 3.0 floor"
claim recorded here on 2026-08-31 applied the wrong floor. The badge that
names the current pass ("sort", "safety", ...) is 12px bold, well under the
WCAG 2.2 large-text threshold (14pt/~18.7px bold or 18pt/24px regular) that
would excuse a 3:1 floor; ordinary text needs 4.5:1. Computed directly
against the real hex values in `App.js` with the actual relative-luminance
formula, not assumed: four of six badge-text colours fell short (sort
3.35:1, safety 3.04:1, standardize 4.01:1, sustain 3.09:1 against the
`#1A272E` screen background). No prior check had ever actually computed
this; `ops/tests/test_mobile_offline_and_a11y.py`, the file the 2026-08-31
note was presumably describing, checks offline behaviour and that every
control carries a role and label, not contrast, so "measured" here meant a
one-off manual count that was never encoded into a repeatable check, the
same "a count stood in for a check" shape `CLAUDE.md` 5c warns against.

Fixed by adding `BADGE_TEXT_COLOUR`, a mapping used only for the badge's
text, lightened along each colour's own hue until it clears 4.5:1 with real
margin (>=4.6). `PASS_COLOUR` itself is untouched and still drives the badge
border (a non-text UI component, 3:1 floor, already passing at every value)
and the finish-screen dots (decorative, already hidden from assistive tech
per the existing test). The pass name is also plain text content on screen,
so colour was never the only carrier of which S is showing either before or
after this fix. New `gate_mobile_badge_contrast` in `ops/preflight.py`
parses `BADGE_TEXT_COLOUR` and `C.deep` straight out of `App.js` and
computes the real ratio, so a future colour change cannot silently
reintroduce this; proved it can fail by reverting one value to its old
PASS_COLOUR equivalent in an isolated check, watching the gate name the
exact colour and ratio, then restoring it and reconfirming clean. Verified
the app itself is unaffected: `npm test` (24 of 24 across 3 files, no
change), `EXPO_OFFLINE=1 npx expo export` for both platforms (iOS 551
modules/1.75 MB, Android 550 modules/1.76 MB, both matching the prior
cycle's own figures exactly), and a grep for network calls still returns
zero. Not verified on a real screen reader or a real device, the same
on-device wall as the rest of 5B.9; this is a source-level colour
correction, not a claim that the on-device half is now closed.

**What is blocked and on whom.** 5B.6 and 5B.10 need an Apple Developer account
and a Google Play account, both of which carry Phil's legal and payment
identity. 5B.7 needs either Java installed on this machine or an Expo account
for cloud builds. 5B.8 needs the accounts layer, which is the same missing piece
that makes 6S Plus unsellable, and is the largest single gap in the whole
business: $11,250 of the $21,500 month 12 model.

**Claiming convention, added 2026-08-31.** Two operators built toward 5B.5 in the same hour without either knowing. Nothing was wasted that time, because verification turned out to be the missing half, but that was luck. Before starting an item, write CLAIMED with the date and which operator into its owner cell and push that line on its own. It costs one commit and it is the only shared signal the two of us have.

**5B.4 finding, 2026-09-01, this operator, from reading `App.js` cold rather
than waiting on the on-device claim above.** The "Not now" button (`skip()`)
called `setFinished(null)` while `finished` was already `null` in every
context that button renders in. React bails out of a state update that is
`Object.is`-equal to the current value without a re-render, so this was not
a small UX rough edge, it was a dead button: pressing "Not now" changed
nothing on screen, ever, on every build since the core loop was written.
Confirmed by reasoning about the exact render path rather than assuming
(the button only exists on the per-card screen, where `finished` is
provably `null`), then proved by building a fix and a failing-first test
around it rather than trusting the reasoning alone. Extracted the card
selection into `lib/pickCard.js`, a pure, skip-aware function mirroring how
`lib/importProgress.js` already keeps merge logic testable without a
device: it now takes a session-only `skipped` map and returns the next
unfinished, unskipped card, falling back to the skipped one if every
remaining card has been passed over, so a player is never left on a blank
screen. `App.js` wired to it, with `skipped` state cleared on the same two
buttons that already reset `session`. New `lib/pickCard.test.js`, 7 cases,
including one asserting the fix's whole point directly: skipping the
current card must return a *different* card, the exact behaviour the old
code never had. Also found and fixed a real gap while adding this:
`lib/importProgress.test.js` has existed since 2026-08-31 and was never
wired into any automated gate, so a regression there would have shipped
silently the same way this bug did. New `gate_mobile_js_tests` in
`ops/preflight.py`, running every `mobile/quest-app/lib/*.test.js` file
found rather than naming these two, proved to fail by breaking one
assertion in `pickCard.test.js` on purpose and watching the gate name the
exact file, restored, reran `preflight.py` clean. Verified the app still
bundles after the change: `npm install` (1,133 packages) then
`EXPO_OFFLINE=1 npx expo export` produced clean iOS (550 modules, 1.75 MB)
and Android (549 modules, 1.76 MB) bundles with no errors, `--platform web`
correctly refused since this app has no web target configured. Does not
close 5B.4: the on-device script and Phil's own scan are still what proves
the loop works on a real phone, but the specific defect an on-device pass
would have found ("nothing happens when I press Not now") is fixed and
gated ahead of that scan rather than left for it to discover.

**5B.4 finding, 2026-09-02, this operator, the same shape one screen over.**
With the "Not now" button fixed, read the rest of `App.js` for the same
pattern (a control whose promise and its `onPress` handler have drifted
apart) rather than assuming one instance was the whole defect. Found it:
the "zone finished" screen offers two buttons, "Draw the next card" and
"Stop here, this counts", and both called the exact same handler
(`setSession([]); setSkipped({}); setFinished(null);`), with nothing to
tell them apart at runtime. The file's own header comment promises "mark
it done, stop without guilt or continue by choice"; the code never
implemented the choice, so every tap forced the next card immediately
regardless of which button was pressed, and there was no way to actually
stop, contradicting the app's own stated design. Confirmed by tracing both
`onPress` bodies rather than assuming from the two different labels.
Compared against the web Quest's own finish screen (`quest.js`'s
`renderFinish()`, wired to `#f-again` and `#f-map`) to check this was a
real gap and not by design: the web version's two finish buttons go to
genuinely different screens (start over, or the room map), so the mobile
app's identical pair is the odd one out, not the norm. Fixed by adding an
`idle` state: "Draw the next card" is unchanged (clears `finished` and
shows the next open card immediately); "Stop here, this counts" now also
sets `idle`, which renders a plain stopping screen (zones held, a single
"Draw a card" button, nothing pushing the player back into another job)
instead of silently doing the same thing as the other button. New
`gate_mobile_finish_actions_distinct` in `preflight.py`, parsing `App.js`'s
own two `Pressable` blocks by `accessibilityLabel` and comparing their
`onPress` bodies as text; proved to fail by reintroducing the exact
original bug shape (removing `setIdle(true)` from the "Stop" handler),
watched it fail naming the real defect, restored, reran `preflight.py`
clean (8 warnings, all standing, same credential and network gaps as
every prior cycle). No React Native test renderer exists in this project,
so this is a targeted source-text regression check, not a rendered
assertion; verified the actual behaviour by tracing the render path
instead. Rebuilt after restoring: `EXPO_OFFLINE=1 npx expo export`
produced the byte-identical iOS bundle hash to the pre-edit build
(`AppEntry-d0f2d5fd965be85317be75df17248974.hbc`, 550 modules, 1.75 MB),
confirming the restore was exact, and a clean Android export (549
modules, 1.76 MB). Does not close 5B.4 or 5B.9's on-device half: still
needs a real phone to confirm the new idle screen actually reads well
with a screen reader and does not feel like a dead end, but the
identical-buttons defect itself cannot ship silently again.

**The honest sequencing.** 5B.1 to 5B.5 and 5B.9 are unblocked and worth doing
now, because a phone-testable core loop is the cheapest way to find out whether
the mobile product is worth the rest of the investment. Everything after that
should wait for evidence from epic 1, which still has no visitor numbers.

**5B.1 done 2026-08-31, this operator.** `docs/audit/CURRENT-STATE-AUDIT.md`.
Read `site/assets/js/quest.js` in full (1,155 lines) and parsed
`quest-data.js` as JSON rather than sampling it: 20 rooms, 114 zones, 684
cards, S-order correct on all 114, matching every public claim. Built a
real, function-level parity table against `mobile/quest-app/App.js` (320
lines): the mobile MVP has the done/skip loop, house-level progress and the
import merge, and is missing mode selection, the timer, photo capture, the
recommendation/sustain engine, streak, the progress map and analytics,
every one grounded in a named function present on one side and absent on
the other, not a guess. `WebFetch` against the live site confirmed the
standing egress wall rather than assuming it; `WebSearch` works but returned
SEO aggregator content for a competitive query, not primary product
documentation, so no competitive-pattern claims are made rather than
fabricating one from low-quality sources. Recommendation: device
verification (5B.4) before more parity building, since an unverified core
loop makes additional features moot. Did not attempt the super prompt's
full nine-file breakdown; the backlog's own acceptance line asks for one
written audit, and nine mostly-empty files would be exactly the bureaucracy
CLAUDE.md warns against. Left 5B.2 and 5B.4 alone: 5B.2 is next and does not
need a device, 5B.4 needs Phil's phone.

**5B.2 done 2026-08-31, this operator, the first unclaimed unblocked row
after walking every epic 1 to 4 item and finding all of them Phil-blocked
or credential-blocked again.** `docs/product/PRD.md` and
`docs/product/WEB-TO-MOBILE-MIGRATION-CONTRACT.md`. Same scope call as
5B.1: the prompt asks for thirteen files, CLAUDE.md section 56 warns
against empty bureaucracy, so this is one consolidated PRD plus the one
document the backlog's own acceptance line names directly, kept separate
because 5B.4 and 5B.5 will want to cite it on its own. Grounded in the
5B.1 audit rather than re-deriving it: read `quest.js` again to confirm
the five recommendation-engine function names cited (`heldZones`,
`daysSince`, `streak`, `nearestZone`, `computeRecommendation`) actually
exist before naming them; grepped `mobile/` and `ops/` for any auth
library before claiming none exists (one false-positive hit, card text
about physical passports, not an auth package); re-ran
`lib/importProgress.test.js` (10 of 10 pass, including the idempotency
case) before writing about it, and caught my own error mid-draft: the
migration contract's first pass claimed idempotency was untested, read
the test file directly, found it already has that exact case, and
corrected the claim before committing rather than shipping a wrong one.
Key decisions recorded: three mobile destinations instead of the prompt's
five (matches the prompt's own warning against three equal walls of
explanation before action), continue React Native/Expo (ratifying what
5B.3 already built rather than reopening a settled call without new
evidence), and the recommendation/audit-due engine ordered first among
the seven parity gaps, since it is the one gap that makes the product's
own stated promise true on mobile rather than a feature-parity nicety.
The migration contract states plainly what most needs saying: there is no
automatic migration, a fresh install starts empty, and photos taken on
web do not travel to the phone through the backup file, only the `done`
timestamps do. `preflight.py` clean after (7 warnings, all standing). No
em or en dashes in either file. Did not touch `App.js` or any other code:
this is the paper work the 5B.1 audit itself recommended proceed now,
while explicitly recommending against starting the parity build-out
(Section 6 of the PRD) until 5B.4 closes, and that recommendation stands.

**5B.5 progressed 2026-08-31, this operator, picking up the exact item cycle
33's own retro named as the highest-value unblocked item left.** Checked
first rather than assumed: the web Quest's backup file
(`site/assets/js/quest.js`'s `backup()`) already writes `{ done: { cardId:
timestamp } }` with the identical `room|zone|pass` cardId shape the mobile
app's own `cardId()` already builds from the shared corpus, so a raw browser
backup needs no translation, only a merge. Built `lib/importProgress.js`
(`parseBackup`, `mergeDone`), mirroring the web app's own `restore()` rule
exactly: the earlier timestamp wins for any card both sides have, so an
import can never erase work already done on the phone. Wired it into
`App.js` behind a new "Already used the web Quest? Import your progress"
link, using `expo-document-picker` and `expo-file-system` (added at the
Expo SDK 51 pinned versions, `npx expo install` itself is blocked from this
sandbox's proxy allowlist, so pinned by hand from `npm view`'s published
versions and confirmed the app still exports clean, which is the real
test). Verified, not assumed: 10 unit tests in
`lib/importProgress.test.js` (run via `npm test`, plain node, no device),
including one that merges a full synthetic house of 684 cards from the real
corpus and confirms nothing is dropped or invented; `npx expo export`
still bundles clean at 548 modules, 1.76 MB, up from 539/1.73 MB only by
the two new native module wrappers. What is not verified from this
sandbox: actually picking a file through the OS document picker on a real
phone, the same on-device wall as 5B.4. The backlog's own acceptance line
("restores into the app with progress intact") is not claimed done here on
purpose; the merge logic it depends on is proven correct, the picker UI is
not.

**5B.5 verification widened 2026-08-31, this operator.** `ops/tests/test_web_to_mobile_import.py`
existed since the note above but had the same defect 6.14 already fixed in
two other files: it only checked the two hardcoded Windows Edge paths, so it
printed "no Edge here, NOT VERIFIED" on every cloud run and never actually
drove anything here. Fixed the same way as 6.14, reusing `ops/browser.py`'s
`find_browser()` instead of reinventing detection. Run for real in this
sandbox against the pre-installed Chromium: it drives the live `quest.html`
in a headless browser exactly as a visitor would, clicks four cards done,
reads the real `localStorage` backup the page's own `backup()` button would
have written, feeds that unmodified text to the mobile app's real
`importProgress.js`, and confirms every card key round trips to a real
zone and pass in the shared corpus with nothing dropped, invented, or
orphaned. This is the first time this exact check has run anywhere in this
project rather than reading "NOT VERIFIED." Proved it can still fail
honestly: forced `find_browser()` to return nothing on a scratch copy,
watched it print the same "NOT VERIFIED" line rather than a false pass,
restored. This still does not close 5B.5: the OS document-picker tap on a
real phone is untouched and stays 5B.4's on-device wall, but the parse and
merge path the backlog's acceptance line actually depends on is now
verified end to end from a real web backup, not only from hand-written
fixtures.

**5B.11 first run, 2026-09-02, this operator, picked up as the only
unblocked, not-started row left in this epic once 5B.4/5B.5/5B.9's code
halves were done and their remaining halves needed Phil's own phone.**
Ran Prompt 9 (`super prompts/6S-SUCCESS-HOME-QUEST-MOBILE-CLAUDE-CODE.md`)
for the first time. Reconstructed current state honestly rather than
re-derive it (step 1): read `App.js`, `lib/pickCard.js`,
`lib/importProgress.js`, `ON-DEVICE-TEST.md`, the 5B.1 audit and the PRD.
Found a real gap: `ON-DEVICE-TEST.md` verified the 2026-09-02 "Stop here"
fix but never verified the 2026-09-01 "Not now" fix, so a full pass of "all
checks green" could have shipped alongside a still-broken fix the script
never actually exercised. Added two checks (a device could report 14 of 14
passing while the exact bug this file exists to catch stayed silent), fixed
the same stale "12 checks" count in `OWNER-ACTIONS.md` and
`APP-DEVELOPMENT-PLAN.md` (both were already wrong at 14, not just now
outdated at 15), and added `gate_on_device_check_count` to `preflight.py`
so a future edit to either side cannot drift again without failing the
gate; proved it fails on the planted stale count in an isolated worktree,
restored, reran clean. Built `lib/eventLog.js` and 7 tests
(`lib/eventLog.test.js`) for the instrumentation bet Prompt 9's step 1
asks for: a local-only, timestamped record of what an install actually did
(card done, skipped, zone finished, stopped, import attempted), wired into
`App.js` behind a new "Diagnostics" text link, so the next on-device pass
produces a checkable record rather than only Phil's memory of what he
tapped. No new network call: grepped for `fetch`/`XMLHttpRequest`/`axios`
before and after, both zero. Verified: `npm test` (24 of 24 across 3
files), `npm install` (1,133 packages), `EXPO_OFFLINE=1 npx expo export`
clean on both platforms (551 iOS modules 1.75 MB, 550 Android modules
1.76 MB), `python ops/preflight.py` clean (9 warnings, all standing, one
fewer than before because the pre-commit hook was also enabled this
cycle). Wrote the eight files Prompt 9 asks for under `docs/future-state/`,
scoped to what this sandbox can actually verify rather than padded: most
business and product-outcome metrics are marked unknown, since zero
installs and no analytics access exist here, per this file's own rule
against inventing a baseline. Selected exactly the prompt's cap of three
bets for next cycle (one primary, one quality, one instrumentation) rather
than opening a fourth. Did not build the recommendation-engine parity gap
or any other feature work: the PRD's own recommendation to wait for the
on-device pass first still stands, and this cycle's own analysis
(`docs/future-state/GAP-AND-ROOT-CAUSE-ANALYSIS.md`) reaches the same
conclusion independently.

---

## EPIC 6: Keep the operation honest

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 6.1 | ~~Inbox agent runs on schedule~~ | owner replies become work items within an hour | 0.3 | **done, verified 2026-08-27** |
| 6.2 | ~~Two agents writing one repo keeps causing conflicts~~ | a rule that prevents it, recorded | 0.3 | **done 2026-08-24** |
| 6.3 | Monthly roadmap review against measured numbers | `ROADMAP-2026-2029.md` reviewed, guesses struck when measured | 0.2/mo | operator |
| 6.4 | ~~15 referenced control documents do not exist (issue #9)~~ | either created or the references removed | 1.0 | **done 2026-08-24** |
| 6.5 | ~~Two documents both named EXECUTIVE-DASHBOARD (issue #8)~~ | one canonical | 0.2 | **done 2026-08-25** |
| 6.6 | ~~Extend the image review gate to card deck art~~ | a generated card sheet cannot reach the live gallery without a recorded "ok" verdict | 1.0 | **done 2026-08-30** |
| 6.7 | ~~Before/after photo import cannot silently delete a room (issue #26 shape, retro's second third)~~ | `ops/import_room_images.py --apply` cannot ship fewer figures for a room than what is already committed, gated in `preflight.py` | 0.5 | **done 2026-08-30** |
| 6.8 | ~~`gate_image_coverage` failed every fresh checkout, permanently~~ | the gate distinguishes "cannot verify freshness here" from "not approved", proved to still fail on a real defect | 0.3 | **done 2026-08-30** |
| 6.9 | ~~Dashboard headline never escalated on a confirmed dead live-links verdict~~ | `dashboard.status_of()` returns RED when `check_live_links.py` reports dead, gated in `preflight.py`, proved to fail | 0.3 | **done 2026-08-31** |
| 6.10 | ~~A confirmed dead live-links verdict was lost on the very next credential-less run~~ | a confirmed "dead" verdict survives an unmeasured run the same way revenue does, gated in `preflight.py`, proved to fail | 0.3 | **done 2026-08-31** |
| 6.11 | ~~A failed git status/rev-list would render as "clean and in sync"~~ | `dashboard.sh_checked()` returns None on a failed git command, `working_tree_status()` reads None as unknown rather than clean, gated in `preflight.py`, proved to fail | 0.2 | **done 2026-08-31** |
| 6.12 | ~~A carried "stale" deploy verdict said "0 of 0 assets differ"~~ | a carried deploy verdict carries its own asset-diff count with it, not this run's own unmeasured default, gated in `preflight.py`, proved to fail | 0.2 | **done 2026-08-31** |
| 6.13 | ~~A shallow clone silently undercounted total commits by 10x~~ | `dashboard.py` attempts an unshallow before counting total commits and reports an explicit unknown rather than the shallow truncated figure, gated in `preflight.py`, proved to fail | 0.2 | **done 2026-08-31** |
| 6.14 | ~~Two functional tests could never actually run in the cloud sandbox, every day~~ | `test_quest_flow.py` and `test_mobile_overflow.py` (via `ops/shoot_mobile.py`) drive the pre-installed sandbox Chromium when Edge is absent, and `preflight.py` warns rather than stays silent when a test file could not verify anything, proved to fire | 0.4 | **done 2026-08-31** |
| 6.15 | ~~Dashboard reported the shipped Entryway deck as "0/88, broken" on every credential-less cycle~~ | `dashboard.py`'s deck line reads the live gallery's real card total instead of a stale hardcoded 88, and distinguishes an unrendered local build cache from an unshipped product, gated in `preflight.py`, proved to fail both directions | 0.2 | **done 2026-08-31** |
| 6.16 | ~~The cycle 29 pre-commit hook was tracked non-executable and could never run on any clone~~ | `.githooks/pre-commit` is tracked mode 100755, and `gate_hooks_enabled()` checks the executable bit in addition to `core.hooksPath`, proved to fail on the real defect | 0.1 | **done 2026-08-31** |
| 6.17 | ~~commits_7d undercounted on a shallow checkout, same bug 6.13 fixed one field over~~ | `dashboard.py` unshallows before counting either commit figure, not only the total, and reports commits_7d as an explicit unknown rather than the shallow truncated number, gated in `preflight.py`, proved to fail | 0.1 | **done 2026-08-31** |
| 6.18 | ~~`status_report.py` reported an unreachable domain as "live" and a sandbox-proxy denial as a real production 403~~ | `domain_state()`/`vhost_state()` never collapse an unmeasured network probe into a specific claim, gated in `preflight.py`, proved to fail | 0.2 | **done 2026-09-01, this operator** |
| 6.19 | ~~The owner's own status report and status PDF still described the pre-launch MVP catalogue~~ | both reports read the real buyable/free/unready counts from the live catalogue instead of hand-typed 2026-08-16-era text, gated in `preflight.py`, proved to fail | 0.3 | **done 2026-09-01, this operator** |
| 6.20 | ~~The four-times-daily roadmap report silently read gh failures as zero open issues, and never checked whether a backlog row was already done~~ | `roadmap_report.py` reports an unreachable `gh` as unknown rather than 0, and `backlog_next()` drops finished rows instead of offering them as still open, gated in `preflight.py`, proved to fail on both | 0.3 | **done 2026-09-01, this operator** |
| 6.21 | ~~`hourly_brief.py`'s BUILD line read two `state.json` key names that never existed~~ | the BUILD line reads the real `open_p0`/`commits_7d` keys via a pure `build_line()`, gated in `preflight.py`, proved to fail | 0.1 | **done 2026-09-01, this operator (row added retroactively, the fix itself predates this row)** |
| 6.22 | ~~`ROADMAP-2026-2029.md`'s own load-bearing price table had drifted from the live catalogue, and `revenue_model.py` had degraded into a 155-row dump~~ | the roadmap's eBook row and the area-bundle price in 3c match the live catalogue, `revenue_model.py` groups by price instead of repeating 109 identical rows, gated in `preflight.py`, proved to fail | 0.3 | **done 2026-09-01, this operator** |
| 6.23 | ~~`corpus_index.py`'s classifier silently dropped 153 finished files into "other", and the dashboard's own corpus count was a number hand typed once in 2026-08~~ | X threads/short-posts and the standalone email newsletter classify as ready, `dashboard.py`'s Social corpus line computes live from `corpus_index.build_index()` instead of a frozen 2,600, gated in `preflight.py`, proved to fail | 0.4 | **done 2026-09-01, this operator** |
| 6.24 | ~~`corpus_index.py` marked x-post/newsletter/linkedin-article files "ready" and `corpus_posts.py` served exactly 0 posts from any of them; separately, 22 already-"ready" linkedin-post/facebook-post entries for paid chapters falsely called the chapter free~~ | the three kinds each serve a nonzero pool, the false-claim filter catches "read the free chapter" phrasing on a paid chapter, both proved by a new test file `preflight.py`'s `gate_tests()` runs and by reverting the fix and watching it fail | 0.4 | **done 2026-09-01, this operator** |
| 6.25 | ~~The same zero-yield defect 6.24 fixed for three kinds still holds for three more: `quote`, `summary`, `takeaways` (153 ready files, 0 usable posts between them). Each is a different shape (a mixed numbered-list-plus-headed-sections quote bank; a doc with 3 summary lengths; a 21-item numbered takeaways list) and needs its own extractor, not a shared one~~ | each kind serves a nonzero pool, same gate extended to cover them | 0.5 | **done 2026-09-01, operator** |
| 6.26 | ~~`ops/linkedin_drafts.py`, the file emailed to Phil every morning, hardcoded "the 18 dollar eBook" in its own "WHAT IS TRUE TODAY" block against a live price of $9.99~~ | the price is read live via `facts()['ebook_price']`, a new `gate_linkedin_drafts_price_current` in `preflight.py` proved to fail on the real defect without mutating the post rotation | 0.2 | **done 2026-09-01, operator** |
| 6.27 | ~~Both owner status reports hardcoded "16" withheld Entryway cards against a live count of 18~~ | `status_report.py` and `status_pdf.py` read the withheld count live from `split_deck_cards.WITHHOLD`, the existing `gate_status_report_products_consistent` extended to prove it, fails on the real defect | 0.1 | **done 2026-09-01, operator** |
| 6.28 | ~~`ops/import_generated_art.py`'s `promote()` silenced `fingerprint_assets.py` with a shell redirect to Windows' null device by name, a literal filename on Linux or macOS, and never checked its exit code either way~~ | the call uses `subprocess.run` with a portable `DEVNULL` and reports a failed fingerprint pass instead of claiming success, `gate_no_windows_only_redirect` in `preflight.py` proved to fail on the real call shape | 0.1 | **done 2026-09-01, operator** |
| 6.29 | ~~`ops/render_cards.py` and `ops/video_zone.py` only ever looked for Windows Chrome/Edge, so both reported "no Chromium browser found" and did nothing on every cloud run, always~~ | both call `ops/browser.py`'s `find_browser()`, verified end to end here: `render_cards.py` rendered and passed all 5 committed card fronts, `video_zone.py` rendered a real non-blank 1080x1920 beat; `gate_browser_detection_portable` in `preflight.py` proved to fail on the real regression shape | 0.3 | **done 2026-09-01, operator** |
| 6.30 | ~~Running `ops/build_manual_print.py` for any reason, including its own `--measure` page count, silently overwrote the manual's real, already-answered copyright and publisher information with `[AUTHOR OR RIGHTS HOLDER]` and other bracketed placeholders~~ | `ops/fill_front_matter.py`'s fill is chained into `build_manual_print.py`'s own `main()`, right after the three manual files are written; a new `gate_front_matter_filled` in `preflight.py` checks the files on disk directly and proved to fail on the real regression shape | 0.3 | **done 2026-09-01, operator** |
| 6.31 | ~~`gate_generator_ownership` was missing `ops/build_avif.py --wire` from its own comparison chain, so it reported the deck gallery pages (both real, both files on disk) as hand-edited drift on every untouched checkout of `main`, always~~ | `build_avif.py` added to the gate's `gens` list with its own `--wire` argument; `ops/tests/test_generator_ownership.py`'s own first assertion (an untouched checkout must not be reported as drift), run for real against a fresh worktree at HEAD, now passes | 0.3 | **done 2026-09-01, operator** |
| 6.32 | ~~`ops/build_kit_page.py` was missing from `gate_generator_ownership` entirely, and its own template carried none of the PWA icons, the progressive marker, measure.js, the skip link, the main landmark id or aria-current, so a rebuild of `kit.html` silently stripped all six and no gate would have noticed~~ | the same seven whole-site wiring passes chained into its own `main()`, `build_kit_page.py` added to the gate's `gens` list; proved by stripping the chain in an isolated worktree and watching the gate name `site/kit.html`, restored | 0.2 | **done 2026-09-01, operator** |
| 6.33 | ~~`ops/build_mobile_corpus.py --check` existed but nothing ran it automatically, so the mobile app's card corpus could go stale against `quest-data.js` with no warning~~ | `gate_mobile_corpus_current` in `preflight.py` compares the committed `mobile/quest-app/assets/quest-corpus.json` against a fresh build every run, proved to fail by mutating the committed file in an isolated worktree and watching it fail, restored | 0.1 | **done 2026-09-01, operator** |
| 6.34 | ~~`ROADMAP-2026-2029.md` section 2's own "known, measured" page count (176, written 2026-08-24) had drifted from the live site (189)~~ | the figure is corrected and `gate_roadmap_prices_current` now checks it against `all_pages()` on every run, proved to fail by reverting to 176 and watching it name the exact drift, restored | 0.1 | **done 2026-09-01, operator** |
| 6.35 | ~~`ops/sync_page_links.py`, the tool that repairs a hardcoded dead payment link, only ever scanned `*.html`~~ | `discover_files()` also scans `*.js`, covering `data.js` (155 links) and `quest.js` (1), a new `gate_sync_page_links_scans_js` in `preflight.py` proved to fail by reverting to the HTML-only glob and watching it name both missing files | 0.2 | **done 2026-09-02, operator** |
| 6.36 | ~~`ops/build_resources.py` was the only generator in `gate_generator_ownership`'s own chain that never ran the whole-site wiring passes every sibling generator runs~~ | `build_resources.py` chains `canonical_links`, `prune_catalog_js`, `wire_landmarks`, `wire_progressive`, `wire_measure`, `wire_pwa`, `wire_aria_current` and `build_avif.wire()` the same way `build_zone_index.py` already does, a new `gate_resources_page_wired` in `preflight.py` checks the committed page directly and was proved to fail on the real regression shape | 0.2 | **done 2026-09-02, operator** |
| 6.37 | ~~`mobile/quest-app/package.json`'s own "test" script never picked up `lib/pickCard.test.js`, only `lib/importProgress.test.js`~~ | `npm test` runs every `lib/*.test.js` file, a new `gate_mobile_npm_test_complete` in `preflight.py` checks the script string against the files on disk and was proved to fail on the real regression shape | 0.1 | **done 2026-09-02, operator** |
| 6.38 | ~~`ops/build_printpack.py` and `ops/build_standards.py`, the $19 Print Pack and the free Standards Pack, were the only two content.json-derived generators absent from `gate_generator_ownership`~~ | both chained into the gate's `gens` list, checked the same way as every site page generator, proved to fail on the real regression shape (a stale committed `build/6S-Whole-House-Print-Pack.html`) | 0.1 | **done 2026-09-02, operator** |
| 6.39 | ~~The committed KDP book cover (`build/cover.png`/`.jpg`) predates the author name being filled into the front matter, and running the generator anywhere but Phil's own machine silently produced an illegible cover that still reported success~~ | `ops/build_cover.py` refuses to write a cover when its named fonts are missing instead of shipping PIL's default-font fallback; `author_name()` is now import-safe (no render side effect); new `gate_cover_author_current` in `preflight.py` compares commit timestamps and fails on the real, current drift, proved to both fail and pass in an isolated worktree; filed as `OWNER-ACTIONS.md` item 12, one command on Phil's own machine | 0.2 | **done 2026-09-02, operator; the "blocked on Phil's Windows fonts" tail is corrected by 6.51 below, 2026-09-03** |
| 6.51 | ~~6.39's own refusal was correct but its premise was not: the Windows font names it looks for were treated as the only legible option, when Liberation Serif/Sans, metric-compatible with Times/Arial and already installed in this sandbox at `/usr/share/fonts/truetype/liberation/`, were sitting unused the whole time~~ | `ops/build_cover.py`'s `font()` tries the named Windows face first, tier by tier, then the matching Liberation face for that same tier before moving on, so the existing Georgia-then-Times-then-Arial preference order is unchanged, only widened; regenerated and committed `build/cover.png`/`.jpg` with the real byline, verified by opening the rendered PNG, not the exit code; `OWNER-ACTIONS.md` item 12 closed as done by the operator, no longer needs Phil's machine; new `ops/tests/test_build_cover.py` proves both directions (a name with a real Liberation face must not trip the missing-font refusal and must return a correctly-sized scalable font, not PIL's own tiny default; a name with no face anywhere still must trip it), proved to fail against the pre-fix generator and pass against the fix | 0.2 | **done 2026-09-03, operator** |
| 6.40 | ~~`gate_cover_author_current`, added the same cycle as 6.39, imported `ops/build_cover.py` at module level, which did a top level `from PIL import ...`; on any machine without Pillow, that raised `ModuleNotFoundError` at import time and crashed all of `preflight.py`, the single gate STEP 2 names, taking every gate after it in `main()`'s list down with it~~ | `build_cover.py` now imports PIL lazily, only inside its own `__main__` render block, so importing it for `author_name()` needs no image library; every one of the 63 gate calls in `preflight.py`'s `main()` now goes through a new `run_gate()` wrapper that catches an exception from any single gate, records it as a named FAIL, and lets the run finish instead of dying; proved in an isolated worktree by planting a crash in `gate_third_party` and watching the run report it by name while every later gate, including the 9 standing warnings, still ran | 0.2 | **done 2026-09-02, operator** |
| 6.41 | ~~`ops/audit_visual.py`'s own docstring claimed its no-arg default covered "every page", but the code globbed only `site/*.html`, the 23 top-level pages, never `site/zones/`, `site/rooms/` or `site/articles/`, the 88 per cent of the site that gate_visual_audit (6.x, deep only) had therefore never once rendered~~ | default now globs `site/**/*.html` (191 pages), matching the docstring; running it against the newly-covered pages found a real live defect immediately: `site/zones/index.html`'s `.zroom`, `.zsession` and `.zchip span` labels read 3.46:1 and 3.57:1 against the 4.5:1 WCAG floor, 233 failing text nodes on the one page every visitor sees before picking a zone; fixed at the source (`ops/build_zone_index.py`) with two colours already used elsewhere on the same page's own palette (`#584f46` 7.5:1, `#3f6647` 6.14:1), both with real margin rather than barely clearing the floor; `gate_visual_audit`'s subprocess timeout raised 300s to 900s so the wider crawl has a real chance to finish in a network-restricted sandbox rather than degrade to "unchecked" every deep run; proved in an isolated worktree: with the fix applied the page audits clean, reverting just the three colours reproduces the original 233 findings exactly, worktree discarded, main untouched | 0.3 | **done 2026-09-02, operator** |
| 6.41 | ~~`ops/build_card_prompts.py` and `ops/build_all_prompts.py` silently substituted a fallback style prefix and an empty already-illustrated set whenever Phil's Desktop was unreachable (every cloud run), so a fresh run here claimed the mudroom deck's 2 real illustrated cards were 0 and would have shipped a different, un-frozen style hash~~ | both writers now call a shared `require_desktop_sources()` and refuse with `SystemExit` naming exactly what is missing instead of guessing; new `gate_card_prompts_desktop_only` in `preflight.py`, proved to fail on the real call site (not merely the function's own name, which a first draft of the gate could never have failed on) in an isolated worktree, restored | 0.2 | **done 2026-09-02, operator** |
| 6.42 | ~~`ops/video_srt.py`, the caption sidecar writer for all 114 zone videos, was never checked by anything: `ops/video_zone.py` renders one video per call with no caption step, `ops/render_all_zone_videos.py` (the batch driver) never calls `video_srt.py` either, and no gate compared a committed `.srt` file against what its own video's beats would produce~~ | new `gate_srt_captions_current` in `preflight.py` regenerates each committed caption from `video_zone.beats()` and fails if it disagrees with the committed file, proved to fail by planting a wrong caption on a real video in an isolated worktree, restored | 0.2 | **done 2026-09-02, operator** |
| 6.43 | ~~Phil's own commit rendered all 114 zone-reset clips a second time at 1920x1080 for YouTube (`build/video/zones-16x9/`), and the dashboard, which had already been fixed twice this week for hiding the vertical and photo-led formats, said nothing about this third one existing either~~ | new `zone_video_16x9_line()` in `dashboard.py`, a fourth distinct table row; `gate_dashboard_zone_video_16x9_live` in `preflight.py` proved to fail on the real regression shape (line rewritten to a nonsense string) in an isolated worktree, restored | 0.1 | **done 2026-09-02, operator** |
| 6.44 | ~~`ops/merge_cardtext.py`'s id-keyed merge silently dropped a real, distinct card (EP-010, Sports Gear Explosion) that had been transcribed under a colliding id (EP-009, the real Mud Trail card's own code), no warning, exit 0~~ | the id corrected at the source in `ops/cardtext/batch-02.json`; `merge_cardtext.load_batches()` now distinguishes a genuine duplicate transcription (same title, needs Phil to read the physical card) from an unexplained one (different titles, a real card hiding behind another's code) and the latter is never silent; new `gate_cardtext_corpus_integrity` in `preflight.py`, proved to fail on the real original bug and pass on the fix in an isolated worktree | 0.3 | **done 2026-09-02, operator** |
| 6.45 | ~~`ops/audit_visual.py` (the contrast/distortion checker built 2026-09-01/02) hardcoded only the two Windows Edge paths, so `preflight.py`'s own `gate_browser_detection_portable` failed against it on every cloud run, and the checker itself had never actually run here, so it caught nothing after the day it was written~~ | fixed to call `ops/browser.py`'s `find_browser()`; running it for the first time in this sandbox found three real, live WCAG contrast defects (`site/deck.html`, `site/invest.html`, and `site/standards.html`'s own generator `ops/build_standards_page.py`), all fixed at the source; new `gate_visual_audit` (deep only) wired into `preflight.py`, proved to fail on a planted regression in an isolated worktree | 0.4 | **done 2026-09-02, operator** |
| 6.46 | ~~`ops/build_youtube_metadata.py` (title, description, tags and timestamps for all 114 zone videos, added by Phil's own commit `d98d1ea` alongside `service_orders.py`) had zero mentions anywhere in `ops/NIGHTLY-LOG.md`, and nothing on the dashboard said the upload text existed, the same hiding-finished-work shape already fixed four times this week for the videos, captions and social cards it sits beside~~ | verified the tool itself first (idempotent: a second run reproduces all 114 files byte-identical to committed); new `youtube_metadata_line()` in `dashboard.py`, a new "YouTube upload text" row on both the markdown and HTML dashboards; `gate_dashboard_youtube_metadata_live` in `preflight.py`, proved to fail on a planted regression in an isolated worktree, restored | 0.15 | **done 2026-09-02, operator** |
| 6.47 | ~~`ops/checkin.py` (`checkin.py` had zero mentions in this log, genuinely unread since it was written) collapsed "could not reach YouTube from here" into "the channel holds None" next to a "Publish" recommendation, live, on this run's own first pass, one cycle after a real session had measured the channel go from 0 to 1; separately, `commits_24h` had no shallow-clone guard (the class `dashboard.py` already fixed twice, 6.13/6.17) and undercounted by exactly one whenever any commits existed (`sh(...).count("\n")` counts newlines, not lines); the "Next" message also hardcoded "228 videos and 114 caption files" as literal text instead of reading the real counts~~ | `checkin.carry_forward()` persists the last MEASURED youtube_published/products_live under their own keys, mirroring `dashboard.py`'s own revenue `carry_forward()`, so an unmeasured run states the real last-known count and its age instead of a false claim; `next_action()` rewritten to take the persisted state and read counts live; `commits_24h_count()` unshallows first and returns None (not a truncated number) if it cannot, and fixes the off-by-one separately; new `gate_checkin_youtube_carry_forward` in `preflight.py`, proved to fail on the exact live bug shape (reintroduced the original `next_action`, watched it render "the channel holds None" next to "Publish" again) in an isolated worktree, restored, reran clean | 0.3 | **done 2026-09-02, operator** |
| 6.48 | ~~`ops/check_sellable.py --deep`'s own live-price check called `stripe_catalog.secret_key()`, which refuses loudly with `SystemExit` when no Stripe credential exists; uncaught, that propagated straight out of `main()` on every credential-less cloud run, so any real defect already collected in `fail` (an orphan buy button, an undeliverable SKU) would have been silently discarded rather than printed or returned, and the crash's own message read exactly like the honest "no credential" warning every other gate in this file already renders, so nobody could have told a real failure apart from a missing key from the output alone~~ | the `--deep` block now catches that `SystemExit` and prints "NOT VERIFIED, could not check live prices" instead of crashing; the fail-collection logic above it, and the final pass/fail verdict, now always run regardless; new `ops/tests/test_check_sellable.py`, two cases, proving a missing credential alone must not fail the run and a real planted undeliverable-SKU defect still fails even when the live-price half also could not run, both in-process against forced state rather than ambient sandbox luck; proved against the pre-fix file too (crashes, exit 1, before either assertion) | 0.2 | **done 2026-09-02, operator** |
| 6.49 | ~~`preflight.py --deep`'s widened visual audit (6.41/6.45) found 401 real WCAG contrast failures nobody had looked at yet: five links on the retired Entryway deck mockup notice page, and 396 repeated instances of four label/note colours across the free 30-chapter sample eBook, the site's primary lead magnet, and the free Standards Pack~~ | all four source colours (in `content/book/assets/book.css`, shared by every book-derived page, and `ops/build_standards.py`) darkened to keep the same hue with real margin over the 4.5:1 floor, computed against each colour's actual background rather than guessed; `--honey` and `--green`/`--spark` themselves left untouched where they are also used decoratively (borders, dots) or correctly on a dark background (`.idea .lbl`), only the failing text rules changed; `ops/audit_visual.py --all` reconfirmed 0 contrast failures across all 191 pages after, up from 401; regenerating `site/downloads/6S Success Home Edition - Sample (Chapters 1-30).html` via its own generator (`ops/build_sample_html.py`) surfaced a second, unrelated real regression caught before committing: the source in `content/book/` never carried the analytics tag or fingerprint hashes the shipped copy had carried since it was hand-finished at ship time, so regenerating from source silently dropped analytics from the site's primary lead magnet with no error; fixed by chaining the analytics tag into the generator itself (same fix shape as issue #26) and re-running `ops/fingerprint_assets.py`, both reconfirmed present in the regenerated file | 0.4 | **done 2026-09-02, operator** |
| 6.52 | ~~`gate_workflows_healthy` had never once actually run anywhere: no `gh` binary in this sandbox, and real CI's runner has `gh` but no token exported to the step, so `gh run list` failed unauthenticated in both places this gate has ever executed~~ | the gate queries the Actions REST API directly with a token from `GH_TOKEN`/`GITHUB_TOKEN` (the same fallback `dashboard.gh_token()` already used for issue counts), `actions: read` and the token wired into both workflow YAML files, proved against real GitHub state (all 8 workflows healthy) and against forced failing/never-run/unqueryable cases in a new test file | 0.3 | **done 2026-09-03, operator** |
| 6.50 | ~~`RISKS.md`, the canonical risk register, had not been reviewed since 2026-08-19 despite its own section 22 promising the CRITICAL entries get re-read every operating cycle; four entries (RISK-0001, 0006, 0008, 0010) had each been resolved by a real, dated, checkable event since then, and the file kept stating the pre-resolution version of each, including its own single most load-bearing sentence, section 24's "the most likely cause is RISK-0001," two weeks after a real transaction made that claim false~~ | RISK-0001, 0006, 0008 and 0010 corrected and closed with current evidence; a new RISK-0013 opened naming the real current constraint (no stranger has ever converted, matching the dashboard's own "discovery, not what can be bought" headline); RISK-0005 updated (the privacy-vs-measurement conflict it was about is resolved, the remaining gap is access, not policy); section 8's summary and section 24's closing claim corrected to match; new `gate_risks_register_current` in `preflight.py`, checking the review date against the file's own monthly promise and the section 8 summary counts against the table beneath them, proved to fail both ways in an isolated worktree | 0.4 | **done 2026-09-03, operator** |
| 6.53 | ~~A `preflight.py --deep` run killed mid-audit by an outer timeout left `site/zones/_visual_probe.html` (a scratch file `audit_visual.py` writes beside the page it is measuring and only removes in a `finally`, which a SIGTERM does not run) sitting in the tree; the next preflight pass picked it up only as a side effect, `audit_pages.py` flagging it as a titleless page and `gate_footer_consistent` separately flagging it as footerless, and the path was not gitignored, so a `git add -A` at the wrong moment would have shipped a bare, unstyled probe file to a real site URL~~ | `site/**/_visual_probe.html` added to `.gitignore`; new `gate_no_stray_probe_files` in `preflight.py` fails if one is ever found sitting in `site/` regardless of cause, proved to fail by planting one and pass once removed | 0.1 | **done 2026-09-03, operator** |
| 6.54 | ~~`ops/affiliate.py`'s `delivered_documents()` globs everything under `site/downloads/*` with no filter, so it can catch `audit_visual.py`'s own scratch `_visual_probe.html` between its write and its `finally`-block cleanup if the two run at overlapping times, which the prior cycle's own "run `--deep` in the background" fix makes more likely, not less; reproduced live: running `python ops/affiliate.py --check` by hand while a backgrounded `preflight.py --deep` had `audit_visual.py --all` mid-flight elsewhere on the site reported "could not read 1 delivered document(s)... failing closed", a false compliance FAIL, and the file was gone a moment later, confirming it was transient scratch rather than a real defect~~ | both of `affiliate.py`'s document globs (the delivered-documents scan and the disclosure scan) skip the exact `_visual_probe.html` basename `audit_visual.py` itself uses, by name rather than by directory, so a real deliverable is never the one skipped; new `ops/tests/test_affiliate.py`, two cases, proving a planted probe file (readable or truncated) is never treated as a delivered document and a real affiliate violation in a document right beside it still fails, proved to fail against the pre-fix `affiliate.py` in an isolated worktree and pass against the fix | 0.1 | **done 2026-09-03, operator** |
| 6.55 | RISK-0007's own mitigation (a timed, end to end restore drill onto a clean target once RISK-0002 is fixed, which it now is) had never been named on any list this operator or Phil actually works from: not `OWNER-ACTIONS.md`, not this file, not `STATUS.md`. Checked directly with grep rather than assumed. | a restore drill runs end to end once a session holds the VPS deploy key, the measured recovery time replaces the assumed one in `DISASTER-RECOVERY.md`, and `RISK-0007` closes with that evidence | 0.5 | operator, needs the VPS deploy key this sandbox does not hold |
| 6.58 | ~~Phil's narration batch (`ops/render_all_narrated.py`) rendered 17/114 zones with real voice and captions under `build/video/zones-narrated/`, 5 posted live on YouTube per commit `42264b13`, and nothing on the executive dashboard said this third video format existed at all, the same hiding-finished-work shape already fixed for three sibling formats~~ | `narrated_video_line()` in `ops/dashboard.py` and `gate_dashboard_narrated_videos_live` in `preflight.py`, proved to fail on a real partial build and pass on a missing/empty one | 0.2 | **done 2026-09-03, operator** |
| 6.57 | ~~`.github/workflows/hourly-brief.yml`'s "Commit the check-in record" step runs `git push origin HEAD:main` but the job declared only `permissions: contents: read`, so every push has failed with a 403 since the workflow was written; `continue-on-error: true` on both the check-in and commit steps hid it behind a green job status, and `git log --all --grep="Hourly check-in"` confirms zero such commits ever reached origin across the workflow's whole history~~ | job permission widened to `contents: write`; new static `gate_workflow_push_permissions` in `preflight.py` fails any workflow that runs `git push` without `contents: write`, no network or token needed, proved to fail on a synthetic broken workflow and pass on the real fixed one | 0.2 | **done 2026-09-03, operator** |
| 6.56 | ~~`ops/experiments.json`'s own `observed_daily_visitors` (what `ops/experiments.py` uses to print how many days a comparison experiment needs at the traffic actually observed) still read 3.4, a 2026-08-24 reading, nine days after `GOALS.md` was corrected 2026-09-02 with a real database pull; `gate_goals_traffic_current` (written that same day for this exact drift shape) checked `STATUS.md` and `ops/roadmap_report.py` against `GOALS.md` but never this file, one sibling over~~ | `observed_daily_visitors` corrected to 1.6 (GOALS.md's 47/30 days), `_traffic_note` rewritten with the real date and superseded reading kept for the record rather than deleted; `gate_goals_traffic_current` widened to check this file too, proved to fail on the real stale value and pass on the fix in an isolated worktree | 0.1 | **done 2026-09-03, operator** |
| 6.59 | ~~`ops/video_narrated.py` and `ops/render_all_narrated.py` (zero mentions anywhere in `NIGHTLY-LOG.md`, so genuinely unread) each computed a zone's filename stem independently rather than sharing one function; `video_narrated.py`'s own `hasattr(vz, "_slug")` check was always False, because `video_zone.py`'s `_slug` was defined only inside `if __name__ == "__main__":` and so was never a real module attribute, silently taking a hand-duplicated fallback every time; `render_all_narrated.py` had a third, separately hand-written copy again. All three agreed on the real 114 zones only because no current room or zone name contains "/" or ",", the exact single-source-of-truth gap that already caused the YouTube metadata slug mismatch (3.10)~~ | `video_zone.zone_slug()` is now the one real implementation; both call sites point at it; new `gate_video_slug_single_source` in `preflight.py`, proved to fail on the real pre-fix regression shape (a synthetic slash-bearing room/zone name produces a literal `/` in the old fallback's filename stem, which `os.path.join` would silently turn into a wrong nested path) in an isolated worktree, restored | 0.1 | **done 2026-09-03, operator** |
| 6.60 | ~~6.59 named five further files as byte-identical style duplicates rather than a live divergence and left them untouched to keep that fix scoped: `ops/build_social_pins.py`, `ops/build_youtube_metadata.py`, `ops/dashboard.py`, `ops/render_all_zone_videos.py` and `ops/video_srt.py` each still carried their own copy of the same slug transform~~ | all five now call `video_zone.zone_slug()` (`video_srt.py` kept its own `slug(room, zone)` name as a thin wrapper, since `preflight.py`'s `gate_srt_captions_current` calls it directly by that name); verified behavior-preserving rather than assumed: regenerated `build/video/youtube/*.json` and `build/video/zones/*.srt` and diffed byte-for-byte against the committed files (identical), confirmed the computed slug matches an existing on-disk social pin filename, and confirmed `ops/state.json`'s video/social counts (zone_videos_built, narrated_videos_built, social_pins_built, youtube_metadata_built, etc.) are unchanged before and after; `preflight.py` fast and `--deep` both clean after, mobile `npm test` 24/24 unchanged | 0.2 | **done 2026-09-03, operator** |
| 6.62 | ~~RISK-0012's evidence cited stale `ops/state.json` values (`forms_dead=14`, `social_units=2600`) against live 188/4,408~~ | corrected both, and `gate_risks_evidence_current` in `preflight.py` checks every `key=value` evidence citation in `RISKS.md` against `ops/state.json` going forward | 0.1 | **done 2026-09-04, operator** |
| 6.63 | ~~`ops/verify_media_delivery.py` (zero mentions in `NIGHTLY-LOG.md`, added by Phil's own `bb9ee6d` the day prior) could not tell "no Desktop delivery folder exists in this environment at all" from "a real file is missing", so it reported every cloud sandbox and CI run (which never has Phil's own Desktop) as a live gap: reproduced directly, running it in this sandbox reported 228 narrated captions "undelivered" against a path that structurally cannot exist here. `ops/checkin.py`'s hourly self check-in ran this every hour and would have shown it as a growing "reliability" alarm the next time the committed caption count changed, the same "cannot check" collapsed into "confirmed bad" shape already fixed once in the same file for `youtube_published`, never carried to this sibling~~ | `verify_media_delivery.scan()` reports `desktop_missing=True` (exit 2) instead of a fabricated count when its Desktop root does not exist; `checkin.parse_undelivered()` turns that into `None` (unmeasured), carried forward under `undelivered_media_last_measured` the same way `youtube_published` already is rather than overwriting the one real reading taken on Phil's own machine; new `gate_checkin_undelivered_media_not_fabricated` in `preflight.py`, proved to fail on the exact pre-fix shape (both files reverted in an isolated worktree) and pass on the fix, and to still catch a real gap when a Desktop folder genuinely exists | 0.2 | **done 2026-09-04, operator** |
| 6.64 | ~~Two concurrent sessions pushed to `main` while this cycle was running (`915adecc`, `4f30b950`), and CI went red on both: `ops/tests/test_generator_ownership.py`'s own "an untouched checkout must not be reported as drift" assertion failed for real, naming `site/standards.html`. Regenerating the page from its own generator (`ops/build_standards_page.py`) dropped `data-sku="PACK-HOUSE"` from the Print Pack buy button that the committed file carries: somebody had hand-patched the analytics attribute onto the shipped HTML (`measure.js` reads `data-sku` to fire buy-click tracking) without fixing the generator that owns the page, the exact issue #26 shape CLAUDE.md 5b warns against~~ | fixed the same one line this operator found (`build_standards_page.py`); a concurrent push from Phil's own machine (`dc25230c`, landed first) fixed the identical line and, checking further than this operator had, found and fixed a second instance of the same missing attribute in `ops/build_zone_index.py`/`site/zones/index.html`. Merged cleanly (identical single-line change on both sides); `gate_generator_ownership`'s existing test is what caught this correctly and stays as the check, no new gate needed | 0.1 | **done 2026-09-04, operator + Phil, concurrently** |
| 6.65 | ~~Two defects found running `preflight.py` cold at the start of this cycle. `gate_dashes` FAILED for real: Phil's own new `REVENUE-REVIEW-2026-09-04.md` (committed 22:12 the night before) carried 7 em dashes, the house style rule `CLAUDE.md` step 5 states as absolute. Separately, `gate_copy_vs_control` warned on two false positives in `shop.html`: `$57.99` is the exact sum of the bundle's three parts, already validated by `gate_bundle_maths`, just stated as "bought separately" rather than "saved"; `$1` was the gate's own regex truncating `$1,200` at the thousands comma, the same missing-thousands-separator shape this gate exists to catch, only inside its own pattern instead of a page~~ | rewrote the 7 em dashes to comma/colon/parenthesis punctuation, preserving Phil's meaning exactly, confirmed with a clean regrep; extended `gate_copy_vs_control`'s regex to match comma-formatted thousands (`\d{1,3}(?:,\d{3})*`) and added a "bought separately" exclusion mirroring the existing "saved" one. Proved both ways in-process rather than assumed: planted a synthetic `$8,432` regression next to a "Buy it now" phrase and watched the gate catch it (proving the comma fix works and the gate can still fail), then confirmed it stayed silent once the file was restored. `preflight.py` fast clean after, 0 gates failed (was 1), 10 warnings (was 11) | 0.2 | **done 2026-09-04, operator** |
| 6.66 | ~~`ops/stripe_fulfil.py` delivers `build/6S-Whole-House-Print-Pack.html` directly to anyone buying PACK-HOUSE. Phil's commit `9e7b1cd1` fixed the card-overflow pagination bug that made the print pack render 152 pages of which 76 were near-empty litter, and its own message claimed "all 155 deliverables were rebuilt," but the committed output of `build_printpack.py` (this one file, distinct from the 155 gitignored `build/products/*.html` `build_catalog.py` owns) still carried the pre-fix geometry. Found running `preflight.py --own`, the CI flag that adds `gate_generator_ownership`; this sandbox's own fast/deep modes never run it (the working tree usually isn't clean enough mid-cycle, and the check itself is slow, 5+ minutes in CI), so a fully clean local `preflight.py` pass had given false confidence that everything shippable had shipped. Every customer who bought the Whole House Print Pack between that commit and this fix would have received the broken version~~ | regenerated the file (76 sheets, matching the fix's own stated proof) and pushed; a concurrent follow-up push from Phil (`f2885908`) fixed it independently the same evening, converged before this push landed. No new gate needed, `gate_generator_ownership` already exists and already caught it correctly in CI; the gap was this operator not running `--own` locally before trusting a push touching a generator-owned deliverable | 0.3 | **done 2026-09-04, operator** |
| 6.67 | ~~That same push still failed real CI on `gate_generator_ownership`, again, over `site/sitemap.xml`, even though this operator had just regenerated it and Phil's own concurrent commit had too. Root cause: `ops/build_seo.py`'s `scan_extra_pages()` walks `site/` with `os.walk()` and sorted the files within each directory, but never sorted the subdirectories themselves, so the top-level traversal order (and therefore the row order of every zone/room/article page in `sitemap.xml`) depended on whatever order `os.scandir()` happens to return on a given filesystem. A long-lived local checkout and a fresh CI clone of the identical commit can walk directories in different orders, so the generator produced a sitemap that agreed with itself on the machine that wrote it and disagreed everywhere else: not a content bug, a determinism bug, and the reason two separate, correct fixes to this same file (this operator's and Phil's) each still failed CI~~ | added `sorted()` around the subdirectory filter in `scan_extra_pages()`. Proved the bug was real and the fix works by monkeypatching `os.walk` to reverse both `dirs` and `files` at each level (simulating a different filesystem's traversal order) and comparing output: the pre-fix logic produced a different page order under the reversed walk (proving the defect), the post-fix logic produced byte-identical output under both orders (proving the fix). Regenerated `sitemap.xml`, confirmed stable across three consecutive regenerations in this environment | 0.3 | **done 2026-09-04, operator** |
| 6.61 | ~~Phil's own commits `6d0094dd`/`bb9ee6d` (2026-09-03) correctly stopped tracking `build/video/*.mp4` in git, delivering rendered video to his own Desktop instead so `.git` would stop carrying 785 MB of regenerable output. The very next credential-less cloud run's dashboard regeneration, inside this same run, silently turned "114/114 rendered", "2/110 eligible", "114/114 rendered" and "75/114 rendered" (this exact sandbox's own real measurement less than an hour earlier, before that commit landed) into "0/114, not yet rendered" across all four zone-video formats, the same hiding-finished-work shape already fixed five times for this family of dashboard line, this time caused by a change in git storage policy rather than a missing feature~~ | `resolve_video_count()` in `ops/dashboard.py`, mirroring `resolve_deploy_verdict()`/`resolve_live_links_verdict()`: a live scan of 0 falls back to the last positive count on record with the date it was actually measured, a fresh scan finding real files always overrides it unconditionally, and an unmeasured run with nothing to carry stays honestly at 0 rather than inventing a number; all four line functions take an optional `carried_from` and print an explicit "(carried forward from ...)" label rather than presenting a carried number as freshly measured. New `gate_dashboard_video_carry_forward` in `preflight.py`, proved to fail by monkeypatching the pre-fix "trust only this run's own scan" behaviour back in (all three assertions failed, naming the dropped count) and pass clean against the real fix, both confirmed in-process rather than assumed. The carry chain itself had already been zeroed by this same run's own earlier preflight calls before the fix was written; restored the last real measurement (114/2/114/75, verified 2026-09-04 00:49, read from the pre-commit `ops/state.json`) into the chain by hand rather than leaving it to reset to 0 on a technicality. `preflight.py` fast and `--deep` both clean after | 0.3 | **done 2026-09-04, operator** |
| 6.68 | ~~GOALS.md corrected its own traffic baseline 2026-09-03 (a mislabelled "47 sessions/30 days" was actually a visitor count; real figures are 52 visitors/144 visits) and `gate_goals_traffic_current` refuses the old wording reappearing in GOALS.md itself. Nothing checked whether STATUS.md's own "why this is YELLOW" narrative and two RISKS.md evidence lists (RISK-0005, RISK-0013) had been told: all three still stated "47 sessions in the last 30 days" as current fact a full day later, the same one-document-corrected-sibling-never-told shape `gate_risks_evidence_current` already catches for numeric state.json citations, just not for this specific retired prose label~~ | corrected all three (STATUS.md, RISKS.md x2), plus two stale code comments (`ops/build_social_pins.py`, `ops/roadmap_report.py`) naming the same retired figure. New `gate_no_stale_session_label` in `preflight.py`, checking STATUS.md and RISKS.md for the retired "N sessions in the last 30 days" wording; proved to fail by planting the exact pre-fix wording back into STATUS.md in an isolated worktree (`FAIL` list named the file), restored and confirmed clean | 0.1 | **done 2026-09-04, operator** |

**6.62 done 2026-09-04, this operator.** `RISKS.md`'s RISK-0012 evidence cited
`forms_dead=14` and `social_units=2600`, both stale against a live
`ops/state.json` of 188 and 4,408: the catalogue and social corpus both grew
since either number was written, neither drift meant the actual problem
(`email_list` still 0) had changed. The identical one-document-corrected-
sibling-never-told shape `gate_goals_traffic_current` already catches for
`GOALS.md`'s traffic figures, just never checked here. Corrected both
numbers, and rather than leave the same gap for the next citation that
drifts, added `gate_risks_evidence_current` in `preflight.py`: it reads
every `key=value` token in `RISKS.md`, keeps the ones naming a real
`ops/state.json` key, and fails on any mismatch, covering every existing
citation (`email_list`, `forms_dead`, `social_units`, `catalog_total`,
`can_take_payment`, `chapters_with_disclaimer`) and any added later, not
just the two found stale this cycle. Proved it both ways in an isolated
`git worktree add --detach`: planted the old stale values, watched it fail
naming both exact mismatches; restored the fix, watched it pass clean.
`preflight.py` fast clean after, 8 warnings (all standing).

**6.52 done 2026-09-03, this operator, found using the GitHub MCP tools directly rather than trusting the standing "gh is not installed" warning to mean nothing could be known.** `preflight.py`'s own `workflows-healthy` warning has read "unchecked" every single cycle since it was written, always attributed to the sandbox missing the `gh` binary. Checked what CI itself sees rather than assuming the warning's own explanation was complete: `publish-image.yml` failed four times in the 36 hours before this cycle (runs 168, 172, 173, 176), and every one of those jobs' own logs shows the identical message, `workflows-healthy: no workflow could be queried (gh unauthenticated or offline)`, from inside real GitHub Actions, where `gh` is pre-installed. The gate has never once been able to look, anywhere, because neither environment exports a token to the step `gh` reads. (The four failures themselves were real, legitimate `gate_generator_ownership`/`gate_browser_detection_portable` catches, each self-corrected the same day; not a new defect, but the only way to know that was to read the actual job logs rather than the run's pass/fail colour.)

Fixed at the root: `dashboard.py` already solved this exact problem for its own issue count (`gh_token()`, `GH_TOKEN`/`GITHUB_TOKEN` from the environment, no `gh` dependency), so `gate_workflows_healthy` now calls the Actions REST API the same way, through a new `_workflow_run_via_api()`, with `_workflow_run_via_cli()` kept as a fallback for a human running this locally with `gh auth login` but no token exported. Wired `actions: read` and `GITHUB_TOKEN` into both `checks.yml` and `publish-image.yml`, the two workflows that actually run this gate; neither exported a token to the step before, so `gh` was unauthenticated in real CI too, not only in this sandbox. Verified against real GitHub state in this sandbox (a genuine token already present here): all 8 workflows queried live, all healthy, gate silent, replacing what had always been a warning. Proved the failure paths rather than only the success path, in `ops/tests/test_workflows_healthy.py`: a forced failing conclusion is named, a forced never-run workflow is named rather than read as healthy, and a total query failure still reads as "unchecked, not healthy" rather than silently passing. `preflight.py --deep` clean after, 8 warnings (down from 10: this one and `hooks-enabled`, fixed the same cycle).

**6.40 done 2026-09-02, this operator, the ninth cycle today, found running STEP 2's own preflight gate before touching anything else, per this file's own rule.** `python ops/preflight.py` crashed outright on a fresh checkout with a bare `ModuleNotFoundError: No module named 'PIL'` traceback from inside `gate_cover_author_current`, added the previous cycle. Read the traceback rather than reaching for a quick pip install: `ops/requirements.txt` deliberately installs nothing but `pymupdf`, with its own header explaining why (it runs inside CI beside `STRIPE_SECRET_KEY` and `SMTP_PASS`, so an unpinned or unnecessary dependency there executes beside those credentials without review), and `gate_cover_author_current` had quietly broken that guarantee by importing a module (`build_cover.py`) whose only reason to need Pillow is rendering, not the `author_name()` read the gate actually calls. Fixed at the source: moved `build_cover.py`'s `from PIL import Image, ImageDraw, ImageFont` out of module scope and into the `if __name__ == "__main__":` block, so importing the module for `author_name()` (what the gate does) needs no image library, while running it directly (what actually renders a cover) still does and still refuses cleanly when Pillow or the Windows fonts are missing. Verified both paths directly: `import build_cover; build_cover.author_name()` now returns `"Philip Kling"` with no Pillow installed; `python ops/build_cover.py` still fails loudly with the same clear `ModuleNotFoundError`, not silently. This did not, by itself, seem worth a new gate: it was one bad import in one file. Widened the read before deciding that, per this file's own step 5c, and found the real gap: `main()` calls all 63 gates bare, with no exception handling, so any one gate crashing has always been able to silently discard every result before it and skip every gate after it, the exact failure just hit. This is the same "fixed in one file, never carried to the class" shape this log has named repeatedly this week, one layer up from a generator or a report script: the class here is `main()`'s own call list. Added `run_gate()`, a thin wrapper that calls a gate, catches any exception, and records it as a `FAIL` naming the gate and the real exception, then rewrote all 63 call sites (including the two that take arguments, `gate_existing(deep)` and `gate_mobile_overflow(deep)`) to go through it. Proved it in an isolated `git worktree add --detach`, copying this cycle's edited files in since they are not yet committed: planted `raise RuntimeError(...)` at the top of `gate_third_party`, ran `preflight.py`, and watched it report `FAIL gate_third_party gate crashed and could not complete: RuntimeError: planted crash for run_gate proof` while all 9 standing warnings and the rest of the run still completed, instead of a bare traceback and exit. Worktree removed afterward; the main checkout was never at risk. Re-ran `preflight.py` clean on the real tree after (63 gates, 9 warnings, all standing credential and network gaps, same as every prior cycle today). No em or en dashes in the diff.

**6.41 done 2026-09-02, this operator, the eleventh cycle today, found by running rather than only reading the last unread prompt-writer files.** `ops/build_card_prompts.py` and `ops/build_all_prompts.py` both read clean on paper, so both were run to verify rather than trusted on sight, per this file's own step 5d. `python ops/build_all_prompts.py` printed a plausible summary and produced a real diff against the committed `build/prompts/ALL-PROMPTS.md`: "90 cards, 0 illustrated" against the committed "90 cards, 2 illustrated," and a different style hash (`e4a66e4c93` against the committed `3766b13583`). Both depend on Phil's Desktop, which does not exist here: `generate_card_art.py`'s frozen Style Bible and a Desktop images folder that says which cards already have art. Neither writer noticed either was missing; `style_prefix()` silently falls back to a generic prefix, and the already-have set silently becomes empty, the same "a generator produces a believable but wrong result outside Phil's machine" shape that has cost real work here before (the zone-hero fallback 6.8 fixed, the illegible cover caught in an earlier cycle today). Caught before committing, per this file's own step 6: read the diff rather than trusting the clean exit code, then `git checkout --` reverted it immediately, nothing staged.

Fixed both writers to call a new `require_desktop_sources()`, defined once in `build_card_prompts.py`, checking both the Style Bible path and the deck's images folder and refusing with `SystemExit` naming exactly what is missing, the same idiom `import_chapter_svgs.py` already uses for its own Desktop-only source. Verified both directions with a fake `$HOME`: refuses cleanly here, and proceeds correctly with fake sources present (1 already-have card correctly counted). New `gate_card_prompts_desktop_only` in `preflight.py`, and a real near-miss inside the gate itself: the first version checked only that the string `require_desktop_sources(` appeared anywhere in each file, which is trivially always true because the shared function's own definition line contains that exact substring, so the gate could never have failed even with the call deleted from `main()`. Caught this in the same isolated `git worktree add --detach` used to prove the gate, before trusting it: planted the removal, watched the first version stay silent, rewrote the check to match the real call sites, replanted both removals one at a time, watched both fail by name, restored, reran clean. Worktree removed afterward; the real checkout was never at risk. No em or en dashes in the diff.

**6.37 done 2026-09-02, this operator, the fifth cycle today, reading the mobile app subsystem end to end per the fourth cycle's own named next step rather than another single `ops/*.py` file.** `App.js` re-read cold for a third time (after the "Not now" and finish-screen fixes two cycles ago) came back clean; no drifted handler this time. `lib/pickCard.js` and `lib/importProgress.js` re-read the same way, also clean, both tests still passing when run directly. The real defect was one file over: `mobile/quest-app/package.json`'s own `"test"` script still read `node lib/importProgress.test.js` alone, written 2026-08-31 when that was the only test file; `lib/pickCard.test.js` was added 2026-09-01 and never added to the script. `npm test`, the project's own documented entry point (named in both `README.md` and this app's own on-device doc), would silently never run it. `gate_mobile_js_tests` already caught a regression in either file directly (it globs `lib/*.test.js`, not the npm script), so this was latent rather than a live gap in what `preflight.py` checks, but it is exactly the "a lesson fixed in one file, never carried to its sibling" shape this log has named repeatedly this week, one layer up: the sibling here is a package script, not another generator. Fixed the script to run both files; ran `npm test` directly and confirmed both suites now execute (17 assertions total). New `gate_mobile_npm_test_complete` in `preflight.py`, checking every `lib/*.test.js` basename appears in the script string; proved it fails by reverting the script to the old one-file version and rerunning `preflight.py`, which named the exact missing file, then restored and reran clean. Also read `ON-DEVICE-TEST.md` in full against the current app: it never exercises the "Stop here, this counts" button added two cycles ago (`idle` state), the newest behaviour in the app and the one most recently proven to have drifted from its own promise once already. Added two checks (13, 14) covering it, with a one-line "what this is for" entry matching the doc's own convention. No em or en dashes in the diff. `preflight.py` clean after (8 warnings, all standing: no Stripe credential, no mail credential, no egress to `6s-success.com` or `api.stripe.com`, `gh` not installed).

**6.36 done 2026-09-02, this operator, found ranking `ops/*.py` by mentions in this log for a genuinely unread file, then widening from the file itself to its siblings once a gap showed up.** `ops/wire_aria_current.py`, `ops/wire_landmarks.py` and `ops/wire_progressive.py` had only one mention apiece; read all three, then checked who calls them rather than trusting they were covered. Six sibling generators (`build_zone_pages.py`, `build_articles.py`, `build_zone_index.py`, `build_deck_gallery.py`, `build_kit_page.py`, `build_standards_page.py`) each chain all three, plus `canonical_links.py`, `wire_measure.py`, `wire_pwa.py` and `build_avif.py --wire`, into their own `main()`. `build_resources.py` chained none of the eight, even though it is in `gate_generator_ownership`'s own `gens` list and is a real, already-rerun generator (5.6's third increment ran it standalone to add per-room Quest links). Verified rather than assumed: reproduced in an isolated `git worktree add --detach`, ran `python ops/build_resources.py` alone, and diffed against the committed page. Real, measured regressions: `<main id="main">` lost its `id` (the skip link's own target, so "Skip to content" pointed at nothing), the `PROGRESSIVE:BEGIN` block was dropped entirely (reintroducing the exact invisible-until-JS failure that block exists to prevent), the header's own `aria-current="page"` mark on the Rooms link was dropped, and every room and zone link gained a hardcoded `.html` suffix disagreeing with those same pages' own extensionless canonical tags. None of this showed up in `gate_generator_ownership`'s own full-chain run, because five other generators later in that same `gens` list happen to run the identical whole-site passes as their own side effect and silently repaired `resources.html` after `build_resources.py` ran; nothing repairs it when this file is run alone, which is how an operator actually reaches for it. Fixed by chaining all eight passes into `build_resources.py`'s own end, same order `build_zone_index.py` already uses. Verified the fix in the same isolated worktree: standalone output now matches the committed page bit for bit on all four properties. Ran it for real in the main checkout too: the whole-site wiring passes touched all 188 pages' `measure.js` reference (stripping the fingerprint `?v=` hash, the documented, expected side effect of running any one of these generators alone), restamped with `ops/fingerprint_assets.py`, and the resulting `site/resources.html` and all 187 other pages came back byte-identical to what was already committed, meaning this closes a latent gap rather than changing anything live today. New `gate_resources_page_wired` in `preflight.py`, checking the committed page directly (`id="main"`, `PROGRESSIVE:BEGIN`, and `canonical_links.rewrite()` for stale `.html` links) rather than trusting chain order to keep masking a regression; `gate_nav_current` already covers the `aria-current` property for every page, so this checks only the three it does not. Proved it fails: planted the exact regression shape in the committed file (stripped the `id`, removed the `PROGRESSIVE` block, restored one `.html` suffix), ran the gate directly, watched it name all three, restored, reran clean. Full `preflight.py` clean after (8 warnings, all standing, same credential and network gaps as every prior cycle). No em or en dashes in the diff.

**6.34 done 2026-09-01, this operator, the 22nd cycle today, 6.3's monthly
roadmap review, timed for the first of the month.** No egress this cycle
(reconfirmed: `6s-success.com` and `api.stripe.com` both unreachable), so
the review that could actually run was against what this sandbox can
measure: the repository itself. `ROADMAP-2026-2029.md` section 1's price
table was already fixed today by 6.22; reading the rest of the document
against real state found one more drift, one section down, the same
hand-typed-and-frozen shape this file's gates have caught nine times this
week in other documents: section 2's "known, measured" line still said
"176 pages live," true when written 2026-08-24, and `len(all_pages())` is
189 now, real growth (articles, `kit.html`, generated content) rather than
an error the original figure made. Corrected the line with an inline note
naming both dates, matching this document's own section 5 convention
("the guess is struck through rather than deleted") rather than silently
overwriting the number. Extended `gate_roadmap_prices_current` (already
the right home: this exact document, the same class of drift) instead of
writing a new gate function, since the check is a two-line addition to an
existing regex-and-compare loop, proved to fail by reverting to 176 in a
scratch copy and watching it fail naming the real drift, then confirmed
restored and `preflight.py` clean end to end (9 warnings before this
cycle's hook re-enable, 8 after). Also spent real time verifying two
claims rather than assuming them, per this file's own step 5d, both
"checked, not a defect": opened the actual shipped
`site/downloads/6S-Entryway-Deck-PrintAndPlay.pdf` at the specific pages
where the withheld Amazon-trademark card (EE-001) and the 16 "Set in
Order" cards (issue #29) would fall in the corpus's own print order, and
confirmed by eye that this PDF renders from the newer, corpus-driven
template pipeline with none of those defects, distinct art from the
scanned-sheet pipeline the live gallery's withholding applies to, matching
what `deck.html`'s own copy already claims; and reran
`ops/optimize_sample_pdf.py --check`, confirming the free sample eBook PDF
is still clean (31.2 MB, 0 PNGs, correct title) from the pass a prior
cycle already applied. Cross-checked the gallery's own 72-shown count
against `WITHHOLD` (18 codes) and found the arithmetic is 90 scanned cards
minus 18 withheld, not 88 minus 18: the corpus (88 written cards) and the
scanned-sheet gallery (90 physical cards) are still two different card
universes, the same two-pipeline gap 2.7 and 5.8 already flag as needing
Phil's decision. Not touched further here.

**6.32 done 2026-09-01, this operator, the 21st cycle today, found by running
`build_kit_page.py` standalone rather than trusting it had never been swept**
(it had 0 references anywhere in `ops/NIGHTLY-LOG.md`). The diff against the
committed page showed six missing whole-site markers at once, the exact issue
#26 shape `build_standards_page.py` and `build_zone_index.py` already closed.
Fixed the same way; verified idempotent (0 diff on a second run of the full
11-generator chain) and proved the gate can fail by stripping the chain call
in an isolated `git worktree`, never touching the real checkout.

**6.29 to 6.31 done 2026-09-01, this operator, picking up cycle seventeen's own
named lead one file further: `ops/video.py`, `ops/build_card_template.py` and
`ops/generated_products.py`'s sibling data files came back clean, so the read
widened to the render and print tools those cycles had left alone as
Desktop-blocked.**

`ops/render_cards.py`, `ops/video_zone.py` and `ops/build_manual_print.py`
all hardcoded only the two Windows browser paths, the exact shape 6.14
already fixed for `test_quest_flow.py` and `test_mobile_overflow.py`. Cycle
sixteen's own reasoning dismissed all four (these three plus `video.py`) as
blocked on Desktop-only source art, which is true of the card and book art
pipelines (`build/heroes/` and the book plates genuinely do not exist here)
but was never actually true of `video_zone.py`: its whole input is
`content/manual/source/content.json` and the brand fonts under
`site/assets/fonts/`, both already committed. Fixed both to call
`ops/browser.py`'s `find_browser()`, the shared lookup 6.14 already built,
and verified rather than assumed: `render_cards.py` rendered and passed all
5 of the committed sample card fronts (Pillow and numpy, needed only by its
own `verify()`, are not in `ops/requirements.txt` and were installed ad hoc
for this one verification, not committed anywhere, since nothing gated
depends on them); `video_zone.py` rendered a real, non-blank 1080x1920 beat
for the Entryway Landing Zone. `build_manual_print.py`'s own `--measure`
step had the identical pattern with a softer failure (a print line saying
"skipping" rather than a crash) and is fixed the same way; it now reports
real pagination (189 pages for the manual and the print edition, 33 for
Appendix A, 11 for Appendix B) instead of silently skipping every cloud run.

**Caught before it shipped: fixing `build_manual_print.py` and running it to
verify surfaced a second, more serious defect, unrelated to the browser fix
itself.** `build_manual_print.py`'s `main()` always rewrites the three
committed manual files, `--measure` or not, and its `COPYRIGHT_PAGE`
constant is a deliberately bracketed template ("a copyright page is legally
material... every bracketed field must be filled... before any commercial
release"). The three committed files already carry the real, correct
answers (Copyright (c) 2026 by Philip Kling, published by Nova Consulting,
4328 North Morninggale Place, Boise, ID 83713), filled in by a separate tool,
`ops/fill_front_matter.py`, that reads `ops/front-matter.json` and patches
its own list of seven target files, the manual's three among them, the same
`ops/front-matter.json` fix 5.7 already applied to `build_epub.py`. Nothing
chained the two together, so the render-tool fix, run to verify itself,
regenerated all three files with the real values overwritten by
`[AUTHOR OR RIGHTS HOLDER]`, `[PUBLISHER ADDRESS]` and the rest. Caught in
`git diff` before committing, reverted immediately, and fixed at the root:
`fill_front_matter.main(True)` is now called from inside
`build_manual_print.py`'s own `main()`, right after the print edition is
written, the same "chain the generator" fix issue #26 and 1.6 already
established for this exact shape. Verified the fix is idempotent, not just
silent: rerunning `build_manual_print.py --measure` after the chain produced
a byte-identical `git diff` against the three committed files, and a new
`gate_front_matter_filled` in `preflight.py` checks the real files on disk
(not that anyone remembered to run a second command), proved to fail by
re-bracketing one real field and watching the gate name it, restored, reran
clean.

**A third, unrelated real finding, surfaced only because verifying the
browser fix meant actually running the full test suite rather than trusting
preflight's own summary.** `ops/tests/test_generator_ownership.py` failed
outright: "an untouched checkout was reported as drift," naming
`site/deck-gallery-mudroom.html` and `site/deck-gallery.html`. Reproduced in
an isolated `git worktree add --detach` at real `HEAD` rather than trusting
the test's own report, per this file's own repeated rule about verifying a
finding before acting on it: `gate_generator_ownership`'s real 11-generator
chain does genuinely report those two files as drifted on a plain, untouched
checkout of `main`. Read the actual diff rather than assuming the pages were
wrong: both differences were `<source type="image/avif">` elements present
in the committed files and absent from what the chain regenerates, and the
referenced `.avif` files genuinely exist on disk (12 for the Mudroom
gallery alone). `ops/build_avif.py --wire` is a real, later, whole-site pass
that adds those sources after the page generators run, the same shape as
`fingerprint_assets.py`, and it was simply missing from
`gate_generator_ownership`'s own `gens` list, the eleventh occasion of issue
#26's pattern: a generator's real output carries content another generator
knows about, and the checker did not know about that second generator. Fixed
by adding `build_avif.py` to the chain with its own `--wire` argument.
Verified in the same isolated worktree, not just read: with the fix, the
chain reproduces both deck gallery files exactly and `gate_generator_ownership`
reports no drift on the untouched checkout; the real, unmodified test file
(not a synthetic gate call) passes its first assertion for the first time.
The worktree was removed and pruned afterward; the main checkout was never
touched by any of this diagnostic work.

**6.28 done 2026-09-01, this operator, the seventeenth cycle today, following
the sixteenth cycle's own named lead: read `ops/build_deck_gallery.py`,
`ops/split_deck_cards.py` and `ops/review_deck_art.py` end to end for the
same shape of drift the report-script sweep had found five times elsewhere.**
None of the three had it: `split_deck_cards.py`'s `WITHHOLD` set and
`build_deck_gallery.py`'s hardcoded `total: 88` agreed with the live
`index.json` (72 cards, checked by loading it directly) and with
`deck.html`'s own honest "72 cards shown, 88 written" copy, so this was a
clean read, not a wasted one. Widened to the fourth file in the same
pipeline, `ops/import_generated_art.py`, since it is the one that actually
calls the other three and had not been read this week either. Found a real
defect there: `promote()` silenced `fingerprint_assets.py` with
`os.system(f'... >nul 2>&1')`. That redirect target is Windows' null
device by name; on Linux or macOS, where every cloud session and the
production VPS run, the shell treats it as a literal filename, so the call
would have written a stray file into the repo root the first time this ran
anywhere but Phil's Windows machine, and `os.system`'s return value was
discarded either way, so a failed fingerprint pass would still have printed
"re-fingerprinted." Confirmed no stray file exists yet (`ls nul` finds
nothing, `git log` shows it was never committed), consistent with this
sandbox never having staged deck art to promote, so the bug is real but has
not fired here. Fixed with `subprocess.run([...], stdout=subprocess.DEVNULL,
stderr=subprocess.DEVNULL)`, checked the return code, and print a warning
naming the exit code instead of a blanket success line on failure. New
`gate_no_windows_only_redirect` in `preflight.py`, a window-based scan
(`os.system(` plus the next 400 characters) rather than a single regex,
because the real call spanned three lines with a nested, already-closed
`os.path.join(...)` in the middle, and a naive `os.system\([^)]*nul\)`
stops at that inner close-paren and never reaches the redirect. Proved it
twice: my own first explanatory comment quoted the broken call almost
verbatim and tripped the new gate against the fixed file, caught by running
the gate before committing rather than assuming a comment is inert;
reworded the comment, reran clean. Then reintroduced the exact original
three-line bug shape in the real file, watched `gate_no_windows_only_redirect`
fail naming `ops/import_generated_art.py`, restored the fix, reran
`preflight.py` clean (8 warnings, all standing, credential and
network shaped as usual).

**6.27 done 2026-09-01, this operator, found reading `ops/status_pdf.py` cold
after the backlog and issue queue turned up nothing newly actionable.** Both
`status_report.py`'s plain text and `status_pdf.py`'s PDF table state
"16 of the Entryway deck's cards are withheld for defective art, issues #1
and #2." Issue #1 (`BRAND_EXCLUDE`, 2 codes, a real Amazon logo baked into
the pixels) and issue #2 (`CANON_EXCLUDE`, 16 codes, the retired "Set in
Order" term and one mislabeled card) are two different sets in
`ops/split_deck_cards.py`; their union, `WITHHOLD`, is 18, not 16. The "16
of...issues #1 and #2" line cites both issues but only ever summed one of
them, an arithmetic drift rather than the deeper two-pipeline
88-vs-90-card total question this file's own 5.8 section already flagged
as needing Phil's decision and not touched here. Verified by importing
`split_deck_cards.WITHHOLD` directly and confirming none of its 18 codes
appear in the live gallery's `index.json` (0 overlap), then fixed both
reports to read `len(WITHHOLD)` filtered to the deck's own code prefix
(the deck name's first letter, matching `split_deck_cards.DECKS`'s own
keys) instead of a typed number, via a new `decks_withheld` computed once
in `status_report.gather()`. Built the actual PDF and read its extracted
text with PyMuPDF to confirm "18 cards" renders, not just that the code
runs. Extended the existing `gate_status_report_products_consistent`
(same shape gate, same two files) to assert the plain text reports 18;
proved it fails by reverting the plain-text line to the literal "16"
string and checking `preflight.FAIL` directly (the gate's own `fail()`
only appends to a list, it does not raise, so an earlier attempt to catch
a `SystemExit` around the reverted code silently reported a false pass;
caught by checking the actual `FAIL` list instead), then restored and
reran clean. Also fixed a real crash the new code introduced: the gate's
own synthetic test dict had no `decks_withheld` key, since `render()` is
called directly in the gate without going through `gather()`, so the
first version of this fix raised `KeyError` inside the gate itself before
reaching any assertion; fixed by making both render sites read
`d.get('decks_withheld', {})` rather than a direct index, and adding the
key to the gate's own synthetic dict so the real wiring is exercised, not
skipped. `reportlab` was missing from this environment even though
`ops/requirements.txt` does not list it; installed ad hoc to build and
read the PDF, not filed as its own item since the package resolved
cleanly and preflight's own bootstrap does not currently install it
either, worth a look if a future cycle hits the same gap.

**6.25 done 2026-09-01, this operator, the twelfth cycle today, the exact
follow-up 6.24 filed as its own item rather than rushing it into that
commit.** Read four real files of each of the three kinds before writing an
extractor, and each turned out to hide a second shape inside the one this
item's own description guessed at. `quote` is not one mixed shape, it is two
separate ones and a chapter uses only one: 34 chapters carry a numbered
"Verbatim lines" list plus several single-quote headings, 16 carry only the
headed quotes, written as a plain quoted line in some chapters and as a "> "
blockquote in others. `summary` is not always the three headed lengths
either: 34 chapters have them, 16 are a single headingless essay of two or
three paragraphs ending in a "Previous: ... Next: ..." chapter-nav sentence
that reads badly as a social post and gets stripped. `takeaways` splits 35
chapters of numbered items with a bold lead sentence against 15 of plain
bullets with no lead at all. Wrote `split_quotes`, `split_summary` and
`split_takeaways` to cover both shapes of each rather than the one shape
each item description assumed, and ran every one of the 51 files per kind
through the real extractor before trusting it, not a sample: 0 zero-yield
files in any of the three. Word bounds for each kind (`quote` 3 to 300,
`summary` 25 to 500, `takeaways` 10 to 200) are read off the actual word
count distribution across the whole corpus, not guessed; the existing 40 to
400 default would have silently rejected most real quotes (many run 4 to 30
words by design, a pull quote is short on purpose) and most bullet-style
takeaways. Yields: `quote` 0 to 904, `summary` 0 to 120, `takeaways` 0 to
807. Checked for the false "free chapter" claim across all three kinds in
chapters 31 to 50 before shipping, the same check 6.24 needed for
`linkedin-post`/`facebook-post`: zero matches, nothing to withhold.

**The same "hand typed and frozen" shape this week's report sweep kept
finding, found once more, one layer under the extractors.** `corpus_index.py`'s
own `units_in()`, which counts how many separate posts a "ready" file holds
for the dashboard's own total, matches only two shapes (`## N.` headed
numbering and `N/` inline numbering), neither of which `quote`, `summary` or
`takeaways` are written in, so all three kinds were silently reporting 1 unit
per file regardless of how many quotes or takeaways it actually held.
Extended `units_in()` to take the file's `kind` and count each shape
correctly (a numbered "Verbatim lines" list plus one per other heading for
`quote`; one per heading excluding "Source files used" for `summary`; the
numbered-bold or bullet count for `takeaways`), falling through to the
existing rules for every other kind unchanged. `dashboard.py`'s own "Social
corpus" line, already wired live to `corpus_index.build_index()` by 6.23's
gate, picked this up automatically on the next regeneration with no
dashboard code changed: postable units rose from 2,721 to 4,408, a real
number this time rather than the old undercounted one.

Extended `ops/tests/test_corpus_posts.py` with both shapes of each new
extractor (8 new synthetic-file cases) plus the corpus-wide nonzero-yield
regression for all three kinds, 17 of 17 passing. Proved `gate_tests()` can
still fail on a real regression: renamed `split_quotes` to break the import,
watched `preflight.py` FAIL naming the exact `NameError`, restored, reran
clean. Scanned every extracted post across the whole live corpus, not a
sample, for leftover markdown (`**`, a stray `> `, an unstripped wrapping
quote mark) and for `TODO`/`TKTK` placeholder text: 0 hits. No em or en
dashes in the diff.

**6.24 done 2026-09-01, this operator, the eleventh cycle today, following up on
the prior cycle's own named next step: extend `corpus_posts.py` to actually
serve the two content shapes 6.23 had just made "ready".** Ran
`ops/corpus_posts.py --stats` live rather than trusting 6.23's classifier fix
was the whole story: `newsletter` and `x-post` both showed 0 usable posts
despite 204 ready files between them, because `corpus_posts.py`'s only
extractor, `split_posts()`, understands one shape (numbered sections under a
`## ` heading) and neither kind is written that way, x-post uses a bare `N/`
line per post, newsletter is one whole document. Read four real files of each
shape before writing anything. Added two new extractors, `split_numbered()`
(strips the trailing `(NNN chars)` line the numbering leaves behind) and
`split_whole()` (one file is one post; strips the sender-only subject/preview
lines and any bare `---` divider), dispatched by kind in `pool()`, with a new
per-kind word-bound table since a newsletter issue or a LinkedIn article is
long-form by design and the existing 40-to-400-word default would reject
almost all of them. Also fixed `linkedin-article` the same way (51 ready
files, also 0 usable, same root cause, found while reading the KINDS table
for what else `split_posts()` was silently failing). `x-post`: 0 to 741.
`newsletter`: 0 to 95. `linkedin-article`: 0 to 47.

**The more consequential finding, surfaced only because making these kinds
servable is what let it be seen: the false "free chapter" claim filter was
too narrow, and it was already live.** Chapters 31 to 50 are inside the paid
eBook; `clean()` has held a filter since before this operator's history here
that discards any post from those chapters claiming the book is free, so a
customer is never told a paid chapter is free. Read the filter's own regex
rather than trusting it was still complete: it only recognised "free online"
and "free in the", not "read the free chapter", "free to read", "free
chapter" or "free copy", phrasing that turned out to be exactly what chapters
31, 32 and 33's own `linkedin-posts-10.md` and `facebook-posts-5.md` files
use ("This is from Chapter 31 of 6S Success: Home Edition. Read the free
chapter."). Broadening the regex to catch the real phrasing dropped
`linkedin-post`'s pool from 324 to 311 and `facebook-post`'s from 164 to 155,
22 posts for paid chapters that were already marked "ready" and already
being served by the live daily-draft path (`ops/linkedin_drafts.py`) before
this fix, not merely theoretical. Checked `ops/corpus-rotation.json` before
treating this as contained rather than assuming: only 3 `linkedin-post` posts
have ever actually been served, and all 3 are chapter 1 (a real free
chapter), so no false claim reached a real draft, but the pipeline serves
oldest-chapter-first and would have reached chapter 31 in the ordinary course
of running. Spot-checked a sample of the newly-caught posts against the real
file content, not just the regex match, to rule out a false positive from the
broadened pattern; all confirmed genuine.

Added `ops/tests/test_corpus_posts.py` (8 cases: both new extractors strip
what they should and keep what they should; the false-claim filter catches
the real phrasing on a paid chapter and correctly allows the same phrasing on
a real free chapter; the newsletter word-bound rejects a too-short body; each
of the three fixed kinds still yields at least one real post). `preflight.py`
already runs every `ops/tests/test_*.py` file via `gate_tests()`, so no
separate gate function was needed; proved the test can fail by stashing the
fix and rerunning preflight (`AttributeError: module 'corpus_posts' has no
attribute 'split_numbered'`, gate FAILED), then restoring and reconfirming
clean. Left `quote`, `summary` and `takeaways` alone (153 more ready files,
still 0 usable, filed as 6.25): each needs a different, more involved
extractor and reading three more real shapes carefully was worth doing
separately rather than rushed into the same commit as the false-claim fix.
No em or en dashes in the diff.

**6.23 done 2026-09-01, this operator, the tenth cycle today, picking up the
prior cycle's own named candidates (`ops/generated_products.py`,
`ops/corpus_index.py`) rather than repeating the price-drift grep.**
`generated_products.py` checked clean (149 sellable, 6 correctly excluded,
math adds up). `corpus_index.py` did not: ran it live rather than only
reading it, and its own docstring number (2,601 files) already disagreed
with the real count (2,875), worth a look on its own before trusting
anything else in the file. 1,550 of 2,875 files classified as "other" with
zero read as ready; opened samples rather than trusting the count. Two real
misses, both verified by reading actual file content before touching code:
`x-thread.md` and `x-short-posts-10.md` (102 files, 51 chapters) are
finished, character-counted X/Twitter posts in the same shape as every
other social kind the classifier already handles, but the existing pattern
(`x-posts|twitter`) matches neither real filename and has never matched
anything in this corpus. `newsletter-version.md` (51 files) is a complete,
publishable email newsletter distinct from `linkedin-newsletter-version.md`
(confirmed by reading one in full, a real ~900 word issue), invisible
because only the LinkedIn-prefixed newsletter pattern existed. Fixed both,
plus `units_in()`, which only recognized `## N.` headings and would have
under-counted every newly-visible X file as one unit each; extended to
also count the `1/`/`1.` per-post numbering those files actually use
(three punctuation variants exist across chapters, found by checking, not
assuming, and all three now match). Ready files: 866 to 1,019. Postable
units: 1,441 to 2,721.

**The dashboard connection, found while checking whether anything besides
`corpus_posts.py` reads this index.** `ops/dashboard.py` has carried
`S["social_units"] = 2600  # corpus size established by audit; not
re-counted each run` since before this operator's history here, rendered
on the executive dashboard as "~2,600 ready-to-publish units, unused",
the exact hand-typed-and-frozen shape 6.18 to 6.22 already found and fixed
five times this week in other files. Wired it to `corpus_index.build_index()`
directly rather than shelling out, so the two numbers cannot drift again by
construction; a failed scan renders "not measured" through a new
`social_units_text()`, never a guessed number, matching the convention
`commits_7d_text()` already established for the same failure shape. New
`gate_dashboard_social_units_live` in `preflight.py`; proved it fails by
reverting the render function to the literal old string, watched it fail
naming all three ways it could be wrong, restored, reran clean. Did not
build the corresponding fix in `corpus_posts.py` (its `split_posts()` only
recognizes the `## N.` post-per-file shape, so the two newly-ready kinds
would report 0 usable posts if run through `--stats` today): that is a
second, larger capability gap (teaching the extractor two more content
shapes, one of them a single whole document rather than a numbered series),
not a misclassification, and worth its own item rather than folded into
this one.

**Also new 2026-09-01, this operator, extending the same "cold-read a
rarely-touched file with real numbers in it" habit from a report script to
the strategy document those reports and this whole routine take their
priorities from.** Ran `ops/revenue_model.py` cold, not just read it, since
`ROADMAP-2026-2029.md` names it directly as the reproduction command for its
own section 1 table. Two real defects, verified before fixing either. First,
the tool itself: written 2026-08-23 against a small catalogue, it still
loops one row per buyable priced product with no grouping, so once 5.7
wired all 155 SKUs live on 2026-08-27 it started printing 188 lines, 109 of
them byte-identical `$4` zone-pack rows, burying the six price points that
actually differ under noise nobody would read past. Fixed by grouping the
table by price, since every product at the same price needs the same order
count against a fixed target; 155 rows collapsed to 11 with nothing lost.
Second, the fact itself: the live price for the Home Edition eBook is $9.99
(set 2026-08-27 alongside the Amazon KDP listing, confirmed by reading
`site/assets/js/data.js` directly), but the roadmap's own section 1 table,
the document calls "the load-bearing claims" in its own closing section,
still read $18 and 1,111 orders, a hand-typed figure the price change never
carried back into. Corrected the row and its downstream order/visitor
numbers; the section's actual conclusion (digital alone cannot carry the
target) does not change, since a lower price needs more visitors, not
fewer, so nothing else in the document was reopened. Checked every other
row in the same table against its SKU rather than assuming only one was
stale: Whole House Print Pack, Micro Zone Manual, Complete Digital Bundle,
Virtual Home Consult and In-Home Reset Day all still match. Found a second,
separate drift doing this: section 3c's "6 area bundles at $24" against a
live `AB-` SKU price of $16, written 2026-08-26 and never revisited; fixed
the same way, with the correction noted inline rather than the old figure
silently deleted, matching this document's own section 5 rule for a
replaced number. New `gate_roadmap_prices_current` in `preflight.py`,
parsing the table's own six rows against the live catalogue by SKU; proved
it fails by reverting the eBook row to the old $18 and watching the gate
fail naming the exact drift, then restored and reran `preflight.py` clean.
No em or en dashes in the diff.

**6.21 done 2026-09-01, this operator, added retroactively.** The fix
itself (a pure `build_line()` reading `hourly_brief.py`'s BUILD line off the
real `open_p0`/`commits_7d` keys `dashboard.py` actually writes, instead of
two names that never existed) was made and pushed the same day, logged in
`ops/NIGHTLY-LOG.md`'s "seventh of the day" entry, with its own preflight
gate proved to fail. That cycle never added a backlog row for it, the one
step 11 of the operating prompt calls for; every sibling discovery this same
day (6.9 through 6.20) has one. Added here so the backlog matches what
shipped rather than silently under-counting this epic's real total.

**6.20 done 2026-09-01, this operator, found cold-reading `ops/roadmap_report.py`
per the prior cycle's own "cold-read one more rarely-touched report" note,
after the day's 9 open issues and 0 PRs reconfirmed nothing new was
GitHub-actionable.** This report is sent to Phil four times a day and had not
been touched since 2026-08-24. Two real defects, both verified by running it,
not by reading it: first, `repo()`'s `gh issue list` call fails outright (`gh`
is not installed in this sandbox) and the old `sh()` swallowed that into `""`,
which `json.loads()` then read exactly like a genuine empty issue list, so the
report printed "0 open issues, 0 labelled decision" while GitHub actually had
9 open, 5 labelled decision, the same unmeasured-collapses-to-a-specific-claim
shape `dashboard.py` (6.9 to 6.17) and `status_report.py` (6.18) already fixed
eleven times over; `roadmap_report.py` had never been swept. Second, and not
the same class: `backlog_next()` had no done check at all, so the live preview
listed 2.9 (the Stripe outage, closed 2026-08-30) under "DECISIONS WAITING ON
YOU" and 1.6 (done 2026-08-29) under "NEXT IN THE QUEUE", both already
finished work presented to the owner as open. Fixed with `sh_checked()`
(returns `None` on any failure, mirroring `dashboard.py`'s own helper),
`open_issues_text()` / `decisions_waiting_text()` (pure render functions), and
`is_backlog_row_done()`, checked narrowly against the backlog's own
strikethrough convention plus an exact "done" in the Est column rather than
any "done" substring, because 5.6's Est column reads "4.0 (1.1 done
2026-08-27)" and 5B.9's Accept column mentions a "done" card state, and both
rows still have real open work that a loose check would have wrongly dropped.
Verified against the real backlog and a real preview run, not synthetic data:
`--edition 8 --allow-partial` now shows 2.9 and 1.6 gone and 2.2 correctly
next. New `gate_roadmap_report_issues_unknown` and
`gate_roadmap_report_backlog_done` in `preflight.py`; proved both fail on the
real defect by reintroducing the old zero-collapse and the old unfiltered
`backlog_next()`, watched each fail with the correct message, restored,
reran `preflight.py` clean.

**6.19 done 2026-09-01, this operator, found reading `ops/status_report.py`
and `ops/status_pdf.py` in full while fixing 6.18 in the same file, rather
than stopping once the network-collapse bug was fixed.** Both reports still
described the catalogue as it existed 2026-08-16: "Three are deliverable
today and all three are consulting", "Deliberately not created: kits,
courses, tools, book, manual", "Both blocked by 13 unfilled front matter
fields, issue #3" (closed 2026-08-25, confirmed by reading the issue rather
than trusting the old comment), "6S Success sandbox, test mode". None of it
is true today: `ops/audit_catalog.py` (0 findings) and `ops/check_sellable.py`
(155 of 155 buyable products in Stripe, with a delivery entry and a file on
disk) both confirm 155 of the 159 live catalogue items already take payment
through a real Stripe Payment Link, and `ops/state.json`'s own `constraint`
field, computed in the same run, already said "158 of 159" two paragraphs
above the stale text. The HTML email summary was the sharpest case: its
"Deliverable today" table row read "consulting only" directly below the
"THE ONE CONSTRAINT" paragraph in the same rendered message, built from the
same `d`/`S` dict, already saying otherwise, the exact copy-vs-copy shape
`CLAUDE.md` names as a P0 trust defect. Fixed by computing
`catalogue_buyable`, `catalogue_free`, `catalogue_unready` and
`catalogue_buyable_other` once in `gather()` from the live `data.js`
catalogue (the same file `audit_catalog.py` checks) plus a `decks` block
read from the live card gallery's own `index.json` rather than the
Desktop-only `deck_rooms` source-folder count, and using those at every
render site in both files instead of hand-typed 2026-08-16 prose. New
`gate_status_report_products_consistent` in `preflight.py`, proved to fail:
reverted the HTML table's row to the literal old "consulting only" string,
watched the gate fail naming exactly that, restored, reran `preflight.py`
clean. Left `ops/send_questions.py`'s own "test mode" line alone: it is not
chained into any automated run (grepped for callers, found none) and is not
part of this report pair; worth the same sweep if it is ever revived, not
done here since fixing dead code without being able to prove it runs would
be a guess.

**6.18 done 2026-09-01, this operator, found running `ops/status_report.py`
cold rather than trusting that a report nobody had reread recently was still
correct.** It printed "6s-success.com  live" and, two paragraphs later,
"Whether 6s-success.com reaches the site could not be checked from this
run's network" in the same report, a direct copy-vs-copy contradiction of
the exact shape `CLAUDE.md` calls a P0 trust defect rather than a polish
item. Root cause: `http()`'s bare `except Exception` defaulted `is_parked`
to `False` (i.e. "confirmed not parked, so live") whenever the request
could not reach the real destination at all, rather than reporting
"unknown." Checked the VPS side rather than assuming the same shape:
`curl -v http://187.77.25.50/` reproduced the report's own "port 80 serves
HTTP Error 403: Forbidden" line, and the response was not from production,
it carried `x-deny-reason: host_not_allowed` and a body reading "Host not
in allowlist", this sandbox's own egress proxy answering in the VPS's
place. The report had been presenting that synthetic denial as a genuine
"vhost for us: NO, falls through to default" production finding. Same
defect class `dashboard.py`'s own gates (6.9 to 6.17) already fixed nine
times over; `status_report.py` had never been given the same treatment,
despite its own docstring already promising "where something cannot be
measured it says so rather than guessing." Fixed `http()` to detect this
sandbox's specific denial signature and return `None` (not `False`) for
anything it could not actually verify, and added `domain_state()` and
`vhost_state()`, pure tri-state functions so every render site (the domain
line, the VPS vhost line, the HTML summary row, the email subject line,
and the "how to publish" and "with the domain parked" paragraphs, all of
which had assumed the pre-launch parked state was still current) reads
"unknown" rather than guessing a direction. Two further stale-copy bugs
surfaced doing this, both fixed the same way: the "To publish the MVP"
checklist printed unconditionally even though the domain has been live
for weeks, and the HTML summary row hardcoded "no vhost for us yet"
regardless of the computed value. New `gate_status_report_network_unknown`
in `preflight.py`, calling the two pure functions with synthetic inputs;
proved it fails by reverting `domain_state(None)` to return `"live"` and
watching the gate go red with the correct message, then restored and
reran `preflight.py` clean. No em or en dashes in the diff.

**6.17 done 2026-08-31, this operator, closing a gap cycle 18 saw once and
left ungated as unreproduced.** `preflight.py`'s own bootstrap run of
`dashboard.py` read `commits7d 52` this cycle, immediately after STEP 0's
branch reset; a real count by hand was 403. Cycle 18 saw the identical shape
once (52 against a real 397) and, correctly at the time, declined to gate a
single unreproduced reading. Reread `dashboard.py` rather than dismissing it
a second time: `S["commits_7d"]` was computed on line 141, straight off
`git log --since="7 days ago"`, three lines before the unshallow attempt
6.13 added, which only ever protected `commits_total` one field below it.
On this environment's normal shallow checkout (issue #27), that let
`commits_7d` silently stop at the shallow boundary and print a small,
plausible, wrong number every single cycle, self-correcting only if
something later in the same run happened to unshallow the repo first.
Fixed by moving the unshallow attempt ahead of both counts and giving
`commits_7d` the same None-means-unknown contract `commits_total` already
had, via a new `commits_7d_text()` pure function used at all four render
sites. New `gate_dashboard_shallow_commits_7d` in `preflight.py`, proved to
fail: broke `commits_7d_text(None)` to return `"0"` (a plausible real count,
not an obvious break) rather than the honest unknown string, watched the
gate fail with the correct message, restored, reran `preflight.py` clean.
No em or en dashes in the diff.

**6.16 done 2026-08-31, this operator, found while acting on a real preflight
failure rather than a routine clean run.** `RETRO-2026-08-31-cycle29.md`
shipped 3 em dashes; the dashes gate caught it, fixed. Enabling
`core.hooksPath` for the same cycle's new pre-commit control-byte hook
surfaced git's own warning on the next commit: the hook was ignored because
it is not set as executable. Checked the tracked mode rather than moving on:
`.githooks/pre-commit` was 100644, so the hook the cycle 29 retro proved
correct three times over could never actually run, on any clone, since it
was written; `gate_hooks_enabled()` only ever checked `core.hooksPath`, never
whether git would honor it. Fixed the tracked mode to 100755 and extended
the gate to check `os.access(hook, os.X_OK)`. Proved it: flipped the bit
off, watched the gate warn with the correct message, restored, confirmed
silent. Full detail in `ops/NIGHTLY-LOG.md`, cycle 13 of the day.

**6.15 done 2026-08-31, this operator, found regenerating the command deck
after nothing else in the backlog was actionable.** `dashboard.py`'s
Entryway deck line read "0/88 cards render clean from the template layer"
this cycle, which reads as the print product being broken. It is not.
Read `ops/dashboard.py` before reporting the number: `cards_rendered`
counts PNGs in the gitignored, per-checkout `build/cards-rendered/` cache
that only `render_cards.py` populates, and only with a real Chromium on
hand; it is empty on every fresh cloud checkout regardless of whether the
actual print-and-play PDF is built. Two problems stacked here: `cards_total`
was hardcoded to 88, stale since issue #29 withheld 16 defective cards from
the live gallery on 2026-08-30 (the real count is 72), and the bare "0/N"
carried no signal distinguishing "nobody has rendered this locally" from
"nobody can print this at all", the same copy-vs-control shape CLAUDE.md
names as a P0 trust defect on the very same deck's other numbers. Fixed by
reading `cards_total` from the live gallery's own `index.json` rather than
a hardcoded figure, and adding a pure `deck_readiness_line()` that reports
"print PDF already built and shipped" when the local cache is empty but
`site/downloads/6S-Entryway-Deck-PrintAndPlay.pdf` exists, while still
reporting a plain "0/N" when it does not, so a genuinely unshipped, unprintable
deck is not silently suppressed. Caught one bug before it shipped: the first
version of the gallery-count read counted the JSON file's top-level dict keys
(3: `deck`, `count`, `cards`) instead of the `cards` list inside it, which
would have shown "3 cards" on the executive dashboard; caught by reading the
actual `index.json` structure rather than assuming a flat list, fixed, and
reran to confirm 72. New `gate_dashboard_deck_readiness` in `preflight.py`,
proved to fail both directions: an unshipped/unrendered deck must still show
the real "0/N" (temporarily removed the shipped-PDF branch, watched the gate
fail with the correct message), and a shipped deck must not read as broken
just because the local cache is empty (the gate's second assertion). Restored
and reran `preflight.py` clean. No em or en dashes in the diff.

**6.14 done 2026-08-31, this operator, prompted by Phil's own cycle 26
retro.** Phil's retro (`RETRO-2026-08-31-cycle26.md`) wrote and verified,
on his own machine with real Edge, a functional test of the Home Quest,
the only complete journey a visitor can finish while every payment link is
dead. Read `ops/tests/test_quest_flow.py` before treating that as settled:
it hardcodes only the two Windows Edge paths, so it has printed "no Edge
here, cannot drive the Quest. NOT VERIFIED." on every single run in this
cloud sandbox since it was written, always exiting 0. `preflight.py`'s own
`gate_tests()` only ever counted a nonzero exit as news, so this read as a
passing test in every cloud preflight run, identical output to a real
pass. `ops/tests/test_mobile_overflow.py` (via `ops/shoot_mobile.py`) and
`preflight.py`'s own `gate_mobile_overflow` had the identical hardcoded
Edge-only check. This sandbox already has a real headless browser
(Chromium, pre-installed at `/opt/pw-browsers/chromium`) that prior
cycles have driven ad hoc with Node Playwright for one-off checks; nothing
had wired it into the standing tests. Added `ops/browser.py`, one shared
`find_browser()` used by all three call sites, returning Edge when present
and falling back to the sandbox Chromium (with `--no-sandbox`, needed only
because this container runs as root) when it is not. Verified end to end,
not assumed: `test_quest_flow.py` now genuinely drives `quest.html` here
and reports the real first-run-to-reload flow; proved it can still fail by
breaking the done button's id and watching it fail with the correct
message, then restored. `shoot_mobile.py` genuinely screenshots and
measures real site pages here now, and still correctly reports a synthetic
900px block as OVERFLOWING. New `gate_tests-unverified` warning in
`preflight.py`: a test file that exits 0 by printing "NOT VERIFIED" reads
identically to a real pass today, the same shape of theatre
`gate_image_coverage` was fixed for in 6.8, so `gate_tests()` now warns
(not fails, since "could not verify" is not the same claim as "broken")
whenever that happens. Proved it fires: temporarily made `find_browser()`
always return `None`, watched the new warning name both affected test
files, restored, reran clean. Left `ops/render_cards.py`,
`ops/build_manual_print.py`, `ops/video.py` and `ops/video_zone.py`
untouched: they render Desktop-only card and book art this sandbox has no
source images for, so fixing their own Edge-only detection would not
unlock any new verification here this cycle, and touching them without
being able to prove it would be a guess, not a fix.

**6.13 done 2026-08-31, this operator.** Same shape as 6.9 to 6.12, one
layer under all four: not a carry-forward bug, a plain miscount.
`S["commits_total"] = len(sh("git log --format=%h").splitlines())` does
not fail on a shallow clone, it just silently stops counting at the
shallow boundary, so this cycle's own dashboard read "56 of 56 total"
commits under "Commits (7 days)", implying the entire repository's
history happened in the last week. Confirmed real: `git rev-parse
--is-shallow-repository` returned true, and `git fetch --unshallow`
revealed the actual total is 575, not 56. Fixed by having `dashboard.py`
attempt a best-effort unshallow (origin is reachable whenever STEP 0
already worked, confirmed this cycle) before counting, and report the
total as an explicit unknown rather than the shallow-truncated number if
unshallowing does not succeed, via a new pure `commits_total_text()`
mirroring `working_tree_status()`'s existing unknown-state handling. New
`gate_dashboard_shallow_commits` in `preflight.py`, proved to fail:
temporarily made the unknown case render as `"0"` instead of the honest
string, watched the gate fail with the correct message, restored, reran
clean. Existing suites still pass (6/6, 4/4). No dashes in the diff.

**6.12 done 2026-08-31, this operator, same class as 6.9 to 6.11, one layer
under the deploy-verdict carry-forward those three cycles already added.**
Read the dashboard's own "What needs you" line rather than trusting the word
"stale" next to it: `resolve_live_links_verdict()` (6.10) already keeps a
carried categorical verdict correct, but the deploy-verdict carry-forward
added the same day only carried the word "stale", not the asset-diff count
behind it, so every credential-less run since 2026-08-30 23:03 has been
overwriting `stale_assets`/`checked_assets` with its own unmeasured `0`,
producing "Production is serving an older build: 0 of 0 assets on the live
homepage differ" under a still-stale headline. Copy and control disagreeing
on the same line is the exact P0 trust defect `CLAUDE.md` names, not a
polish item. Fixed with `resolve_deploy_verdict()`, a pure function mirroring
`resolve_live_links_verdict()`: a real measurement always wins, and a carried
verdict carries its supporting numbers with it.

The first version of this fix pinned the one-time backfill to a specific
committed timestamp string, and a same-cycle merge with a sibling session's
own regenerate-the-deck commit broke it immediately: that session had real
egress, measured a genuinely fresh "stale" at 4 of 4 with a new timestamp,
but is running a `dashboard.py` that predates this fix, so its own
`state.json` only ever recorded the number inside the nested `deploy` dict,
never the flat keys the pinned backfill looked for. Caught by rereading the
generated line after the merge rather than trusting the earlier fix, and
corrected by widening `resolve_deploy_verdict()` itself to fall back to the
nested dict when the flat keys are absent, rather than pinning to one
timestamp: this holds for any sibling session's real measurement, not only
the one already on record. `gate_dashboard_deploy_carry_forward` gained a
third case covering exactly this shape (a real number recorded only in the
nested dict). Manually repaired `ops/state.json`'s asset counts twice this
cycle, both times after a test or a merge overwrote them before the correct
fix was in place; each repair is called out here rather than folded away,
since a carry-forward mechanism whose own tester can silently erase the
figure it protects is worth remembering. Proved the final gate can fail by
reverting the fix and watching it go red with the correct message, then
restored and reran clean, then confirmed three consecutive blind
`dashboard.py` runs hold 4 of 4 steady. Existing suites still pass (6/6,
4/4). No dashes in the diff.

**6.11 done 2026-08-31, this operator, same class as 6.9 and 6.10 one layer
earlier: the git status/ahead fields, not the live-links or revenue fields.**
Read `ops/dashboard.py`'s own comment above the GitHub-issues fetch ("a failed
API call must never render as zero open issues... reporting UNKNOWN when the
answer is one subprocess away is worse than not having the panel") and checked
whether the git block six lines above it followed its own rule. It did not:
`S["clean"] = sh("git status --porcelain") == ""` and `S["ahead"] = sh(...) or
"0"` both used `sh()`, which swallows a failed command into the same empty
string a genuinely clean tree or zero-ahead count produces, so a git failure
(no `origin/main` ref reachable, the exact "unrelated histories" checkout state
issue #27 names, hit again at the start of this cycle) would render as "clean
and in sync" instead of the true "could not be checked." Fixed with
`sh_checked()`, which returns `None` on a nonzero exit or a raised exception
instead of `""`, and `working_tree_status()`, a small pure function so
`gate_dashboard_working_tree` can prove the decision without shelling out.
Proved the gate can fail on the real mechanism, not a toy case: temporarily
reverted `sh_checked()` to the old swallow-to-`""` behavior, watched the gate
fail with the correct message ("a git failure would collapse into the same
value a real, empty success produces"), restored, reran `preflight.py` clean.
Existing unit suites still pass (6 of 6, 4 of 4, 9 of 9). No site content
touched.

**6.10 done 2026-08-31, this operator, same day as 6.9 and the same class of
defect one layer earlier.** Watched it happen rather than reasoning about it:
this cycle's own first `preflight.py` run silently overwrote the committed
`ops/state.json`'s `live_links_verdict` from `"dead"` (measured 2026-08-30
19:23 by a session with real Stripe access) to `"unknown"` (this sandbox has
no Stripe credential), and the dashboard's own headline visibly dropped from
RED to YELLOW between the two commits, nothing about production having
changed. 6.9 taught `status_of()` to escalate on a dead verdict; nothing
taught the verdict itself to survive a run that could not re-measure it, so
the fix from six hours earlier could not fire on the one case that matters
most: an outage that stays open across a string of credential-less cloud
cycles, which is exactly this environment's normal state. Fixed with
`dashboard.resolve_live_links_verdict()`, a pure function mirroring the
existing `carry_forward()` revenue pattern: only a run that actually reaches
Stripe may overwrite the standing verdict, and only `"dead"` is ever carried
forward, never `"ok"`, so an unmeasured run cannot borrow old good news the
way it can honestly keep old bad news. Backfilled the two new persistence
keys from the last real measurement in git history (`cca414e`, 2026-08-30
19:23) since they did not exist before this fix; self-sustaining from here
on, verified across three consecutive dashboard runs. New
`gate_dashboard_live_links_carry_forward` in `preflight.py` calls the pure
function with synthetic inputs and checks both directions: a carried dead
verdict must escalate `status_of()` to RED, and a carried `"ok"` verdict must
never be reported as freshly reconfirmed. Proved it fails: disabled the
carry-forward branch, watched both the gate and the real dashboard headline
drop to YELLOW together, restored, reran clean. Caught one own-goal before
committing: the new function's name briefly collided with a fragile regex in
`ops/tests/test_carry_forward.py` that extracts `carry_forward`'s source by
name prefix, which silently grabbed the wrong function and broke that test;
renamed to `resolve_live_links_verdict` to clear the collision, reran the
test to confirm 6 of 6 cases still pass.

**6.9 done 2026-08-31, this operator.** With almost every backlog item still
Phil-blocked or credential-blocked this cycle (re-verified rather than
assumed: no egress to `6s-success.com` or `api.stripe.com`, confirmed again
via the proxy's own status endpoint; no Search Console tooling or credential
exists either, so 1.5 is not actually operator-actionable despite reading as
unowned), regenerating the command deck (`ops/dashboard.py`) surfaced a real
defect worth reading rather than a routine run: `status_of()` computed the
dashboard's headline RED/YELLOW/GREEN verdict from `can_take_payment` (a
static scan of the repository) and open P0 count, but never looked at
`live_links_verdict`, the actual measured state of whether Stripe's live
payment links are dead. Reproduced by monkeypatching
`check_live_links.check()` to return `"dead"`: the headline stayed YELLOW
("3 P0 items still open") while the body two lines down already read "NO,
live payment links are deactivated in Stripe", copy and headline
disagreeing, which CLAUDE.md's own rule treats as a P0 trust defect rather
than a polish item. Fixed by making `status_of()` a pure function
(no closure over the module's global `S`) so its exact real logic can be
unit tested with synthetic inputs, and adding a RED branch on
`live_links_verdict == "dead"` ahead of the P0 count check. New
`gate_dashboard_severity` in `preflight.py` calls the real `status_of()`
with a synthetic dead verdict and 0 open P0s and fails if the result is not
RED; proved it can fail by temporarily removing the new branch and watching
the gate go red with the correct message, then restoring it and confirming
`preflight.py` is clean again. Also tried, and failed the same way a prior
cycle did: re-attempted `update_trigger` on issue #27's hourly trigger with
the already-drafted STEP 0 fix (unshallow before the fast-forward merge),
confirmed the exact same fast-forward still works this cycle after
unshallowing (260 commits, clean, zero data loss), but the tool still
refuses because this session did not create that routine. Commented on
issue #27 with the re-confirmation rather than re-filing; no repository
change possible from this session's side.

**6.8 done 2026-08-30, this operator.** `preflight.py` FAILED this cycle
with "110 page(s) carry a photograph, 110 advertise one as their preview,
0 images are approved" (`gate_image_coverage`, added a prior cycle per its
own docstring). Read the check rather than trusting the number: it
re-verifies approval by sha-hashing the source pictures in
`build/heroes/zones/`, which is gitignored on purpose and only ever
populated on Phil's own machine during an active image-review session
(confirmed again this cycle: 0 files present, same wall as the 1,000
existing images and the zone-hero generator itself). Verified by hand,
without the source pictures, that the live site is actually fine: every
one of the 110 wired stems matches a `verdict: "ok"` entry in the
committed `ops/hero-verdicts.json` by name, 0 discrepancies. So the gate
was not catching a defect; it was structurally unable to pass in this
sandbox and would have failed every future cloud cycle on nothing.
Fixed `gate_image_coverage` to fall back to verdict-by-name verification
when `build/heroes/zones/` has no source files (an environment signal,
not a review outcome), keeping the strict sha re-check for when a real
review session's source pictures are present. Proved the fallback can
still fail: flipped one real stem's recorded verdict to `"reject"` and
watched the gate go red with the correct stem named, then restored it.
`preflight.py` now passes clean with an honest warning explaining why
freshness could not be re-checked here, instead of a false FAIL.

**6.7 done 2026-08-30, this operator, the before/after-pairs third of the same
retro note 6.6 closed the card-deck third of.** Read `ops/import_room_images.py`
rather than trusting the retro's blanket "no equivalent gate" as still true
of this pipeline: it is not the same shape of risk as the zone-hero or
card-deck generators. Those generate new, unreviewed AI art on every run, so
they needed a human verdict gate. This one copies real photographs from the
book that a person already selected and captioned, via a finalization-notes
process recorded on disk per chapter, so a review-verdict step would be
theatre here, not a fix, and I did not build one. What it actually needed:
running it (not just reading it) showed every room's source path resolves
through `content/book/*/chapter_N_final.html`, and in any environment
without that room's real image on disk (this sandbox, for all 9 committed
rooms; specifically also chapter 39's own mirror, which currently carries 0
JPG `<img>` figures at all, only inline SVGs, while 3 of Kids Bedroom's
figures are already live and committed), a plain `--apply` used to write an
empty or shrunken manifest over the real one, silently deleting up to all 41
already-shipped figures on the next commit. Fixed with `reconcile()`: the
script now keeps a room's already-committed entries whenever the source
yields fewer, and prints a warning naming which rooms it preserved rather
than applying blind. Added `gate_room_images_stable` to `preflight.py`,
checking both that every committed entry's file still exists on disk and
that `reconcile()` cannot regress a room; proved it can fail by disabling
the preservation logic and watching the gate go red on this exact repo
state, before restoring it. Chapter 39's own source gap is unexplained and
unfixed, since its real cause is outside this sandbox either way (Phil's
own master, or a mirror that needs correcting); this only makes it
impossible for that gap to reach a commit as data loss. The chapter-figures
third of the retro's original note (`ops/import_chapter_svgs.py`) is a
different shape again, already imported one figure at a time with each one
individually read per the 3.3b note above, and is not started as an
equivalent-gate item; not evaluated this cycle beyond confirming it is a
manual, per-figure process rather than a bulk rerun risk.

**6.6 done 2026-08-30, added by this operator, not in the backlog until now.**
`RETRO-2026-08-30.md` (Phil's own retrospective on the zone-hero incident) named
the gap directly: "The card decks, the before and after pairs and the chapter
figures all run through generators with no equivalent gate." Read
`ops/import_generated_art.py` rather than trusting that as a finding: confirmed
it copied a finished card sheet straight into the deck source folder and
rebuilt the gallery in the same run, checked only by size, aspect ratio,
flatness and a banded-edge proxy for baked-in text, none of which can tell a
correct card from a garbled or mismatched one, the same gap the zone-hero
`verify()` step had. Fixed by staging sheets under `build/deck-review/<deck>/`
instead of publishing them, and adding `ops/review_deck_art.py`, the same
contact-sheet-and-verdict pattern as `ops/review_heroes.py`, sha-checked so an
approval cannot outlive the picture it was about. `ops/import_generated_art.py
--apply` now stages new drops and separately promotes only sha-matched "ok"
verdicts, on every run, not only the run that happened to see a new file.
Verified end to end with synthetic card sheets (this sandbox has no Desktop
and no real card art to test against, the same wall as the zone-hero pipeline):
an unjudged sheet stays off the gallery, a rejected one stays off it, an
approved one promotes and rebuilds correctly, and a bare `--apply` with
nothing new but an existing approval still promotes it. Testing this also
surfaced a false alarm worth recording rather than repeating: a synthetic
Desktop folder holding only the one test file made the mudroom gallery appear
to drop its two real cards down to one, which looked exactly like the class of
defect this file warns about elsewhere. It was not one: `split_deck_cards.py`
rebuilds a deck's whole gallery from every source sheet in Phil's Desktop
folder, which in production accumulates every card ever generated, so the
apparent loss was this sandbox's incomplete test fixture, not the pipeline.
Confirmed and reverted before committing anything. This closes the card-deck
third of the retrospective's ask; the before/after photograph pairs and the
chapter figures still run without an equivalent gate and are not started.

**6.7 done 2026-09-02, added by this operator, not in the backlog until now.**
Reading `ops/video_zone_photo.py` end to end (per the fourth cycle's own
plan to sweep the video/PDF pipeline once single-file `ops/*.py` sweeps ran
dry) found the same hiding-finished-work shape 3.10 already fixed once for
the typographic zone-reset clips, one layer deeper: `ops/video_zone_photo.py`
renders a second, photo-led format of the same short zone-reset video, built
from a zone's own approved hero picture, with 2 already committed under
`build/video/zones-photo/`. Nothing on the executive dashboard said this
format existed at all. Fixed with `zone_photo_video_line()` in
`ops/dashboard.py`, the same pure-function shape as `zone_video_line()`, a
new "Zone reset videos, photo-led" row in both the markdown and HTML
dashboards, and `gate_dashboard_zone_photo_videos_live()` in `preflight.py`.
The eligible pool is zones with an approved hero (110), not all 114, since a
zone with no reviewed photo can never produce one of these. Proved the gate
fails by breaking the line's format string and watching preflight name it,
restored with `Edit` rather than `git checkout --` after a first attempt at
that command discarded the whole feature (the file had no prior commit this
session to fall back to cleanly), reran clean.

---

## What is deliberately not in this backlog

- **A $99 digital tier.** The $49 bundle already contains every digital asset
  that exists. It would be the same files with a bigger number on them.
- **Paid acquisition.** Buying traffic into a funnel that has never converted a
  stranger converts money into noise.
- **A second illustrated deck.** The free Entryway deck exists to produce
  evidence first. It has not produced any yet.
- **A subscription.** Needs the same impossible volume, plus accounts and a
  backend that do not exist, and there is no evidence anybody wants recurring
  value from a tool for finishing your house once.
- **Publishing `the_call` and `watch_for` as standalone pages.** Proposed and
  rejected on 2026-08-24: that content already ships as FAQPage questions on the
  canonical zone pages, so it would be 114 pages competing with themselves.

## Items waiting on Phil, consolidated

1. **Umami share URL or API key, wired into `ops/dashboard.py`** (1.1, corrected
   2026-09-02). Not a full block any more: Phil read the analytics database
   directly on 2026-09-02 (the API token is expired) and got a real one-time
   baseline, recorded in `GOALS.md` and `STATUS.md` section 9. What is still
   his to do is a share URL or key an operator session can read without him,
   so the baseline refreshes itself instead of going stale between manual
   pulls.
2. **Listmonk sending identity** (2.1). Decide: separate instance, or change the
   global from-address and accept the cost to the other brand.
3. **Publish the ten LinkedIn posts** (3.1). Already written and in his inbox.
4. **Generate the nine tier-0 images** (3.3). Prompts ready.
5. **Chapter 47 monochrome plates** (2.5), **card deck sales model** (5.1).
6. **Stripe business website field** (2.8, issue #21). Settings, Business
   details, Public details, Edit. Everything else on the account (name,
   statement descriptor, support email/URL, legal pages, checkout branding)
   is already fixed per account; only this one field was blocked by Stripe's
   own safety check when the operator tried it, because it can silently
   change Ledgerium's account too. Also worth a decision while there: the
   industry/MCC code (Software, wrong for books and consulting) and whether
   to keep Stripe Climate's 1% contribution.
7. **The 1,000 existing images** (3.3b). Found 2026-08-26: not reachable from
   this sandbox, same as the credentials above. Needs the 864 book plates, 90
   deck illustrations and 94 photographs placed somewhere this operator
   environment can reach, or a session with that access doing the import.
8. **Google Business Profile** (3B.2). Needs a phone number, which does not
   exist anywhere in the written record yet (a free Google Voice number
   would do), plus five minutes to create and verify the listing under his
   own account. Everything else, the description, category and exact
   service-area towns, is drafted at `build/gbp-listing-package.txt`.
9. **Apply to retail affiliate programmes.** Link layer, compliance gate and
   primary-sourced research on all 10 candidate programmes are done
   (2026-08-28, Phil's own commits); `build/affiliate-email.txt` is the
   dossier. Opening an account carries his legal/tax identity, so applying
   is his step, not the operator's. Do not apply to Amazon or Wayfair per
   the dossier's own findings; Etsy, Office Depot and the legacy Home Depot
   programme look like the best near-term fits.
10. **Referral partner outreach** (3B.3). Three message templates (senior
    move managers, real estate agents, professional organizers) and a
    response log are ready at `build/referral-partner-outreach.txt` and
    `build/referral-partner-outreach-log.csv`. Needs him to find 20 to 30
    real local contacts and send the messages under his own name or
    LinkedIn account; also his call on whether to offer any compensation
    for a referral, which the templates deliberately leave open.
