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
| 1.1 | **Umami read access** | `ops/` can fetch visitor counts without a browser login | 0.2 | **Phil**, 3 clicks |
| 1.2 | Wire the share URL or API key into the dashboard | `python ops/dashboard.py` prints real visitors, not "not measured" | 0.5 | operator |
| 1.3 | Answer EXP-001: has a stranger ever clicked a buy button | a number in `ops/experiments.json`, `observed_daily_visitors` no longer null | 0.5 | operator |
| 1.4 | Answer EXP-002: does anyone reach the offer at the bottom of a zone page | scroll depth distribution recorded for 30 days | 0.3 | operator |
| 1.5 | Search Console: first impression data | 30 days of impressions exported and read | 0.5 | operator |
| 1.6 | ~~Wire measure.js and PWA icons into the 134 room and zone pages (issue #28)~~ | `ops/wire_measure.py`/`wire_pwa.py` report 0 skipped for `site/rooms/` and `site/zones/`, verified in a headless browser | 0.3 | **done 2026-08-29** |

**1.1 is the single highest value item in this document.** Everything in epics 3
and 4 is guesswork until it lands.

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
| 3.4 | Measure whether images change anything | before/after comparison on those 3 pages after 30 days | 0.3 | operator, needs 1.1 |
| 3.5 | Second wave of images if 3.4 is positive | 30 more images live | 3.0 | conditional on 3.4 |
| 3.6 | ~~Internal link depth audit~~ | every zone page reachable in 3 clicks from home | 0.5 | **done 2026-08-24** |
| 3.7 | Article expansion, only on measured queries | new articles written against real Search Console queries, never invented ones | 2.0 | needs 1.5 |
| 3.8 | Directory and citation listings, only legitimate ones | listed where a real human would look for this | 1.0 | operator, see note |

**3.7 is deliberately blocked on 1.5.** Writing articles against guessed queries
is how a content site accumulates pages nobody searches for.

**3.8 was researched and deliberately not executed, 2026-08-24.** No verified
physical location exists for local directories, generic submission lists skew
toward low-quality link schemes, and actual submission means creating accounts
under the business's identity on third-party sites, which is worth Phil's
awareness first. Full reasoning in `GROWTH-PLAYBOOK.md` section 4. Revisit if a
specific, clearly legitimate, niche-relevant directory is identified.

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
| 3B.2 | Google Business Profile for the service area | live, verified, linked from consulting.html | 0.5 | operator |
| 3B.3 | Referral partner outreach: agents, senior move managers, organizers | 20 to 30 real contacts made, responses logged | 2.0 | **Phil** makes contact, operator drafts |
| 3B.4 | Run the test to its stop date | pass or fail recorded against G2 below, either way | 1.0 | operator |

**3B.1 is a financial commitment and therefore not mine to make.** CLAUDE.md
puts material spending in the RED band. The recommendation is a few hundred
dollars and a hard stop at 90 days, reported pass or fail, not left open ended.

---

## EPIC 4: Conversion (do not start before epic 1)

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 4.1 | EXP-003: free artifact first vs method first | powered sample reached or 6 weeks elapsed, result recorded either way | 1.0 | needs traffic |
| 4.2 | Offer placement, if EXP-002 shows nobody scrolls | offer moved, measured, kept or reverted | 0.5 | conditional |
| 4.3 | Post-purchase sequence | a buyer receives a second useful email, not a pitch | 1.0 | needs 2.1 |
| 4.4 | Cart abandonment: there is no cart | decide whether checkout sessions can be recovered at all | 0.3 | operator |

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

## EPIC 6: Keep the operation honest

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 6.1 | ~~Inbox agent runs on schedule~~ | owner replies become work items within an hour | 0.3 | **done, verified 2026-08-27** |
| 6.2 | ~~Two agents writing one repo keeps causing conflicts~~ | a rule that prevents it, recorded | 0.3 | **done 2026-08-24** |
| 6.3 | Monthly roadmap review against measured numbers | `ROADMAP-2026-2029.md` reviewed, guesses struck when measured | 0.2/mo | operator |
| 6.4 | ~~15 referenced control documents do not exist (issue #9)~~ | either created or the references removed | 1.0 | **done 2026-08-24** |
| 6.5 | ~~Two documents both named EXECUTIVE-DASHBOARD (issue #8)~~ | one canonical | 0.2 | **done 2026-08-25** |

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

1. **Umami share URL** (1.1). Three clicks. Unblocks five items.
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
8. **Apply to retail affiliate programmes.** Link layer, compliance gate and
   primary-sourced research on all 10 candidate programmes are done
   (2026-08-28, Phil's own commits); `build/affiliate-email.txt` is the
   dossier. Opening an account carries his legal/tax identity, so applying
   is his step, not the operator's. Do not apply to Amazon or Wayfair per
   the dossier's own findings; Etsy, Office Depot and the legacy Home Depot
   programme look like the best near-term fits.
