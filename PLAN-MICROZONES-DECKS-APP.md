# Plan: micro zones, decks, and the web app

**Owner:** `product-manager`. **Written 2026-09-07.** This is a plan, not an
implementation. Nothing outside this file was changed to produce it.

**Direction from Phil, verbatim:** expand on the micro zone concepts and
"decks", improve the web app based on micro zones, and always include detailed
information on all 6S activities for all micro zones.

**Read first:** `GOALS.md` (the constraint is arrivals),
`REVENUE-REVIEW-2026-09-04.md` (do not add products), `DECK-SYSTEM.md` (what a
deck is), `CLAUDE.md` sections 6, 15 and 52.

Every number below was measured today against `content/manual/source/content.json`,
`ops/cardtext/kitchen-deck.json`, `ops/card_spec.py`, `site/`, or is carried
from a dated measurement in another control document and says so. Every
unmeasured belief is labelled a hypothesis and carries its evidence tier from
`CLAUDE.md` section 15.

---

## 0. The one-page answer

The six passes are complete. All 684 slots (114 zones x 6) exist in
`content.json`; none are missing. So "expand the micro zone concept" cannot
mean *more instructions*, because the instruction side is finished.

What is missing is the other half of our own model. `CLAUDE.md` section 6 says
root cause before solution, and the product model runs
`Values -> Room -> Function -> Micro Zone -> Outcome -> Friction -> Root Cause
-> Activity -> Quest -> Standard -> Sustain`. Measured against the corpus:

| Link in the model | Where it lives today | Coverage |
|---|---|---|
| Personal values | nowhere | 0 of 114 |
| Room primary function | room intro prose, not selectable | 20 of 20, prose |
| Micro zone | `content.json` `zone` | 114 of 114 |
| Desired outcome | `purpose` + `done_looks_like` | 114 of 114 |
| **Current friction** | **only `ops/cardtext/kitchen-deck.json`** | **7 of 114** |
| **Root cause** | **29 articles, linked identically everywhere** | **0 of 114 mapped** |
| 6S activity | `passes` | 684 of 684 |
| Quest | `quest.js`, one card per pass | 684 of 684 |
| Standard | `leave_behind.standard` | 114 of 114 |
| Sustain | `passes.sustain` | 114 of 114, median 28 words |
| Who uses it | prose, incidental | 11 of 114 name a user |

**The product diagnoses for seven micro zones and prescribes for all 114.**
That is the expansion: build the diagnostic layer, not a seventh S and not a
115th zone.

Three consequences, in the order I would do them:

1. **The diagnostic layer is also the only item here that plausibly touches the
   constraint.** 114 x 3 frictions is 342 question-shaped strings on 114 pages
   Googlebot already fetches (178 fetches in 72 hours, `GOALS.md` 2026-09-05).
   Everything else in this plan is below the constraint.
2. **Sustain is the measurable content gap and it is worse than "thin".** It is
   not a short pass, it is a *restatement of a field the page already prints*.
   Section 2.
3. **The next deck ships without pictures.** The text is written and gated; the
   art is the expensive, twice-failed part. Section 3.

---

## 1. Expanding the micro zone concept

### 1.1 Measured today, so the plan is not arguing with a guess

| Fact | Value | How measured |
|---|---|---|
| Zones | 114 across 20 rooms | `content.json` |
| Six-S slots present | 684 of 684 | word count on every `passes` key |
| Shine surfaces | 749 | sum of `shine_detail.surfaces` |
| Zones with a friction layer | 7 (Kitchen, in the deck JSON) | `kitchen-deck.json`, 21 `FRICTION CARD` |
| Zones with a mapped root cause | 0 | no such field exists |
| Zones naming who uses the zone | 11 of 114 | regex over the whole zone record |
| Zone pages with the **identical** 19-link "Related reading" block | **110 of 114** | parsed all 114 pages; 5 distinct link sets exist, one covers 110 |
| Quest cards whose "You can stop when" is the whole-zone end state | **570 of 684** | `quest.js` sets `#c-done-look` to `c.zone.done`, which is `done_looks_like`, reachable only after all six passes |

Evidence tier for all of the above: **tier 2, verified product data**, measured
2026-09-07.

### 1.2 What a micro zone should carry that it does not

Four new fields per zone. Nothing existing is rewritten.

```
diagnosis: {
  frictions: [ 3 x { symptom, prompt, branches: [ { answer, cause } x3 ] } ],
  causes:    [ 2-4 x cause_id from a frozen 17-item vocabulary ],
  users:     { who, reach_or_height, child_access, conflict },
  first_15:  { action, minutes, inputs, victory }
}
```

- **`frictions`** is the symptom in the household's own words, and the branch to
  why. Not "clutter accumulates" but "I wipe it on Sunday and by Tuesday it is
  gone again", which is the shape already proven in the Kitchen deck.
- **`causes`** draws from one frozen vocabulary shared by the deck, the app and
  the articles, so a household is never taught two names for one thing. The
  Kitchen deck already uses twelve of them; the full list in the product model
  is seventeen (corrected 2026-09-07, this operator: the twenty-one written
  here was DECK-SYSTEM.md's own friction-card count for the Kitchen deck,
  not a root-cause count; see M1 below and `ops/root_causes.py`).
- **`users`** is who the zone is for, their reach and height, whether a child
  has to work it alone, and where two people want two different designs. 95 of
  114 zones mention reach *somewhere* in prose; 11 say who uses the zone.
- **`first_15`** is the smallest useful action with an observable victory, so a
  zone has an entry that is not "45 to 75 minutes, six passes".

**Why this helps a real household.** Today the app tells someone to Sort their
prep counter. It never asks why the counter refills. If the real cause is that
the things landing there have no home elsewhere, Sort produces four clear days
and one conclusion: this method does not work. Diagnosis is the difference
between the second week and the first. This is our own stated principle
(`CLAUDE.md` section 6) and we do not currently obey it in the product.

**Why it also touches the constraint.** The 29 articles are already the
root-cause layer in prose, already shaped like real queries ("why does mail
always pile up by the door"), and 110 of 114 zone pages link all 19 of them
identically. That is simultaneously the worst possible internal-link signal
(every zone endorses every article equally, so no article receives a topical
signal from any zone) and a near-duplicate block on 114 pages. Replacing it
with 3 to 5 links chosen by the zone's actual causes costs nothing new to write.

### 1.3 What a micro zone **page** should contain that it does not

In order down the page:

1. **A diagnosis block above the six passes.** "Which of these is true here?",
   three frictions, each opening to a named cause, a 30-second confirmation
   test, and which pass to start at. Today the page opens with a 45-to-75-minute
   session length and assumes all six passes in order.
2. **The 15-minute entry**, named, with its victory condition.
3. **Who uses it**, including reach, child access, and the two-user conflict
   where one exists.
4. **A Sustain block worth the name.** Section 2.
5. **Related reading chosen by cause**, 3 to 5 links, not the same 19.

### 1.4 What a **card** should contain that it does not

- **A victory condition for that card.** Right now 570 of 684 cards print the
  whole-zone `done_looks_like` text rather than a victory reachable by that
  one pass. **The honesty part of this is fixed** (Phil, `fa491b1a`,
  2026-09-07): the heading no longer claims that state is the stop condition,
  it says what the text is and where the reader stands against it. What
  remains is a genuinely distinct authored line per card (M7), still unstarted
  and correctly so, per this section's own ordering.
- **One line of why this pass, in this zone**: the cause it treats.
- **On the Sustain card, an artefact.** Section 2.4.

### 1.5 Work items

| # | Item | Why | Tier | Days | Acceptance criteria | Owner |
|---|---|---|---|---|---|---|
| **M1** | ~~Freeze the root-cause vocabulary (21 causes) and map each to the article that explains it~~ | one name per cause across deck, app, articles, pages | 2 | 0.5 | **Done 2026-09-07, operator.** `ops/root_causes.py`, `gate_root_cause_vocabulary` in `preflight.py`, `ops/tests/test_root_causes.py` (7 cases). The 21 above is corrected to 17: `DECK-SYSTEM.md` line 242's "21 KF-001..021" names 21 FRICTION cards in the Kitchen deck, not 21 root causes, and this row's own count was read off that line without checking which noun it counted. The real total is the Kitchen deck's own 12 (`KC-001`..`012`, copied character-for-character, name and `six_s` cross-checked against `kitchen-deck.json` by the test) plus 5 more evidenced by name in `site/articles/` content that no Kitchen zone needed (`RC-013`..`017`: unclear ownership, sentimental attachment, unresolved decision, difficult to clean, perceptual blindness), not padded to a number nobody had measured. Every article reference resolves to a real file. Gate proved to fail on a planted unknown id in an isolated worktree, restored. | product-manager, done by operator |
| **M2** | ~~Add the `diagnosis` schema to `content.json` and a validator~~ | the corpus is the single source; the book, pages, app and deck all build from it | 2 | 0.5 | **Done 2026-09-07, operator.** `ops/diagnosis.py` + `content/manual/source/validate.py` GATE 8. First draft gave each friction one flat `cause`; corrected same cycle after checking it against the real `kitchen-deck.json` FRICTION CARDs, which branch one symptom to two or three different causes (KF-001 alone branches to KC-002, KC-001, KC-008), matching the acceptance text's own wording, "a **branch** naming an unknown cause". `start_pass` was dropped rather than added: every cause in `ops/root_causes.py` already carries the pass it belongs to (`six_s`), so a second copy per friction would be one more place for the two to drift apart. `ops/tests/test_diagnosis_schema.py`, 9 cases, including 3 of the real Kitchen deck's own friction cards run through the schema unmodified. Gate proved to fail on a planted regression run against the live corpus in memory (unknown cause, too few frictions, missing victory, 3 problems named), corpus untouched. Zones without `diagnosis` still build (0 of 114 diagnosed today; `validate.py` passes). | software-engineer, done by operator |
| **M3** | ~~Author `diagnosis` for the 12 pilot zones: Entryway 5 + Kitchen 7~~ | these are the only 12 zones with a published video, i.e. the only ones with any distribution surface (`GOALS.md`, 12 of 228 published) | 2 | 1.5 | **Done 2026-09-07, both halves.** Kitchen half done by a concurrent operator session (`3e58d480`): all 7 Kitchen zones pass `ops/diagnosis.py`, every string copied verbatim from `kitchen-deck.json`'s own FRICTION and 15-minute ACTION cards. Entryway half done this session, reconciled onto that tip rather than re-pushing a conflicting `content.json`: the 5 Entryway zones were hand-authored, grounded directly in each zone's own already-published `passes`/`the_call`/`watch_for` text (no equivalent card deck exists to reuse from), every cause drawn from `ops/root_causes.py`'s frozen 17, no fact invented. All 12 zones now pass M2's validator (`content/manual/source/validate.py` GATE 8: 12 of 114 diagnosed, 0 problems). New `gate_diagnosis_authoring` in `preflight.py` asserts on every run that the 7 Kitchen zones' 21 frictions reuse a real FRICTION CARD's `title` or `objective` and branches character-for-character, and scans every diagnosed zone anywhere for a customer/reviewer attribution claim; `ops/tests/test_diagnosis_authoring.py`, 5 cases, proves both defect classes get caught on a planted mutation. `content.json`'s Entryway diff is a verified pure addition (259 lines, 0 changed), confirmed by a controlled round-trip before editing. | content-editor, done by two operator sessions |
| **M4** | ~~Render diagnosis on those 12 zone pages, with `FAQPage` entries for the frictions, and swap their related-reading block to cause-chosen links~~ | new question-shaped text on already-crawled pages; this is the one item aimed at the constraint | 2 | 1.0 | **Done 2026-09-07, operator.** `ops/build_zone_pages.py`: `diagnosis_html()` renders the "Which of these is true here?" block above the six passes for all 12 pilot zones (each friction's symptom, every branch's answer with a 30-second confirm test and which pass to start at, plus the `first_15` quick entry); `diagnosis_faq(thing, zone)` adds one FAQPage Q&A per friction; `cause_reading(zone)` replaces the shared 19-link block with 3 to 5 articles chosen by the zone's own diagnosed causes (`ops/root_causes.py`'s `article` field), in friction order, capped and deduplicated. Verified against the built output, not assumed: all 116 JSON-LD blocks on `site/zones/*.html` parse; exactly the 12 diagnosed zones carry `id="diagnosis"`; all 12 related-reading sets are pairwise distinct and each holds 3 to 5 links; the other 102 zones are byte-unchanged in substance (still the general 19-link block, still no diagnosis block). Not checked against the live domain itself, per `CLAUDE.md` 0.3: this sandbox has no egress to 6s-success.com, same wall every prior cycle has recorded; needs a session with real access, or Phil's own view of the site once deployed, to confirm the served page matches. Two real defects caught before shipping, both by reading the rendered output rather than trusting a clean exit code: a `symptom.lower()` in the first draft of `diagnosis_faq()` turned "how often I sort it" into "how often i sort it", and `_norm_symptom()`'s use of `str.capitalize()` on an all-caps Kitchen symptom did the same to a mid-sentence "I" ("I BUY SPICES I ALREADY OWN" to "I buy spices i already own"). Both fixed; new `gate_diagnosis_rendered` in `preflight.py` (`ops/tests/test_gate_diagnosis_rendered.py`, 8 cases) checks render coverage, the 3-to-5 link range, cross-zone uniqueness, and this exact pronoun defect on every future run, proved to fail on five planted regressions including the real one this cycle shipped twice. Full test suite (41 files), `content/manual/source/validate.py` GATE 8, `audit_pages.py` (191/0), `audit_catalog.py`, `check_urls.py` (187/187) all clean after. | ux-frontend + seo-aeo, done by operator |
| **M5** | ~~Kill the identical 19-link block on the remaining 102 pages~~ | 110 of 114 pages currently carry byte-identical related reading | 2 | 0.5 | **Done 2026-09-09, operator.** `general_reading()` in `ops/build_zone_pages.py` scores each of the 19 `ZONE_READING` articles against each non-diagnosed zone's own already-published text (its judgement call, all six passes, its hazards), using grounded keywords (the article's own title/description, plus the root cause's own `meaning` where one exists) and an IDF-style weight, nothing invented for the purpose. Deterministic regardless of Python's hash-randomised string/set iteration (a first draft summed over an unsorted set intersection and produced a different pick on roughly 1 run in 5 depending on `PYTHONHASHSEED` alone, caught before it reached the corpus; `ops/tests/test_general_reading.py` proves this across 4 seeds). Verified against the real, generated pages, not assumed: all 114 zone pages (102 general-reading plus 12 M4 cause-reading) carry 3 to 5 links, 0 duplicate sets across the whole site, every one of the 19 articles keeps between 16 and 33 site-wide inbound zone links (diagnosed-zone usage counted in the same tally). A small, disclosed tradeoff: the plan's own stated ceiling of 30 binds tightly against the harder requirement (no duplicate sets) for 5 of 102 zones, whose own text is thin enough that most articles score near zero (two patio zones among them); a deterministic post-pass swaps their lowest-scoring pick to preserve uniqueness even when every under-cap alternative is exhausted, landing 3 articles at 31 to 33 rather than 30. New `gate_general_reading_differentiated` in `preflight.py` re-derives the same picks fresh from `content.json` on every run and checks both that the corpus-level result holds M5's criteria and that the shipped pages actually carry it, mirroring `gate_diagnosis_rendered`'s two-layer pattern for M4; `ops/tests/test_gate_general_reading.py` (12 cases) and `ops/tests/test_general_reading.py` (determinism, idempotency, size/uniqueness) both fail-then-pass proved by planting a render mismatch and watching the gate name it. Article inbound-link concentration dropped from avg 76.3 (min 1, max 124) to avg 26.6 (min 1, max 47) across all 29 articles, `ops/link_graph_report.py` confirms 0 orphans introduced. Full `preflight.py`, all 58 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (163 documents) all clean after. | seo-aeo, done by operator |
| **M6** | Author `diagnosis` for the remaining 102 zones | completes the layer | 2 | 4.0 | All 114 pass M2. **Gated:** do not start until M4 has been live 21 days and `analytics-intelligence` reports whether the 12 pilot pages moved on impressions or entrances against the other 102. | content-editor |
| **M7** | Per-card victory conditions for all 684 cards | fixes the 570-card defect in 1.1 | 2 | 1.5 | Every card in `quest-data.js` carries its own `victory`; `#c-done-look` reads it; the whole-zone `done_looks_like` appears only on the Sustain card and on the zone page. A reviewer can confirm each victory is achievable by that pass alone. **Honesty defect fixed 2026-09-07, Phil, `fa491b1a`; full acceptance criteria not met, correctly not started since.** Phil's own commit found the exact problem this row describes (a card headed "You can stop when" printing the whole-zone `done_looks_like`, unreachable by one pass alone) and fixed the lie rather than authoring 570 new lines under traffic pressure: the heading now says what the sentence is ("The whole zone is done when"), and a second line places the reader against it ("This card is pass N of 6, so you are not aiming for all of it right now"). Verified 2026-09-09, this operator, by reading `site/assets/js/quest.js` (`renderCard()`) directly rather than trusting the commit message: the relabel and the note are both live, on every non-Sustain card, and the simplified first-card override (A4) already carries its own real per-action `victory` line from `diagnosis.first_15`, so that path never shows the shared text at all. What is not done, and should not be started yet: a genuinely distinct authored victory line for each of the 570 cards this row originally counted (the A4 override only swaps in a real per-action victory for whichever single card a first-time visitor's symptom pick happens to open that session; it adds no `victory` field to the underlying card data, so the 570 count is unchanged), which is real product-tier work (`GOALS.md` rule 1, distribution beats production) with no traffic yet to justify it. New `gate_quest_card_victory_honesty` in `preflight.py` (`ops/tests/test_gate_quest_card_victory_honesty.py`, 6 cases, fail-then-pass proved by reintroducing the exact old heading live and watching it fail by name) protects the honesty fix itself from regressing while the deeper content work stays correctly held. | content-editor + software-engineer |

**Deliberately not in this section:** a values selector, a room-function
selector, and a household-conflict survey. They are the most attractive part of
the product model and they are entirely below the constraint: they add a
questionnaire in front of a product that 51 of its last 53 visitors left without
finishing anything. Revisit when the app has a working first thirty seconds and
somebody is finishing cards. See section 5.

---

## 2. The Sustain deficit

### 2.1 What was measured, today

| Pass | Median words | Mean | Min | Max | Under 30 words |
|---|---|---|---|---|---|
| Sort | 46 | 47.3 | 34 | 75 | 0 |
| Straighten | 44 | 44.4 | 25 | 66 | 1 |
| Shine | 40.5 | 41.6 | 24 | 73 | 4 |
| Safety | 51 | 51.9 | 29 | 134 | 1 |
| Standardize | 37 | 37.4 | 23 | 55 | 18 |
| **Sustain** | **28** | **28.9** | **16** | **50** | **73** |

And the part that matters more than the word count:

- **2 of 114** Sustain passes name a cadence (daily, weekly, monthly).
- **5 of 114** name who owns it.
- **2 of 114** say what to do when it has slipped.
- **17 of 114** are more than 60% textually identical to that zone's own
  `leave_behind.trigger`, a field the zone page already prints separately under
  "Reset trigger". The worst is 86% identical.

Tier 2, measured 2026-09-07.

So Sustain today is one sentence: a trigger plus a small action. The shortest is
sixteen words. That is not a sustain system, it is a reminder, and Sustain is
the S that turns a reset into a method. Without it every other pass we ship is
a one-off clean, which is the exact thing our own marketing says we are not.

### 2.2 What a good Sustain pass contains

Six elements. The first is all we have today.

1. **Trigger.** An event that already happens, that the reset attaches to.
2. **Cadence.** How often, matched to how fast this zone actually degrades. A
   sink is daily; a garage overhead bin is annual. Getting this wrong is its own
   root cause (Wrong Frequency).
3. **Owner.** Who does it, and what happens the week they are away. A standard
   with no owner is a preference.
4. **The reset, timed.** The specific physical thing, in under a stated number
   of minutes, small enough that it survives a bad week.
5. **The drift signal.** The first visible sign it is slipping, named as an
   object, before the zone collapses. "Two mugs on the counter at bedtime" is a
   signal. "It gets messy" is not.
6. **Recovery.** What you do when it *has* slipped, which must not be "run the
   whole zone again". If recovery costs 45 minutes, nobody recovers.

For shared zones, a seventh: **what the household does when it fails twice**,
because the second failure is a design problem, not a discipline problem
(`CLAUDE.md` section 10: an ordinary household problem is not a character
defect).

### 2.3 What it takes to bring all 114 up

Schema first so it is machine-checkable, then author in room batches, and prove
the shape on 12 zones before committing four days to the other 102.

| # | Item | Why | Tier | Days | Acceptance criteria | Owner |
|---|---|---|---|---|---|---|
| **S1** | Add `sustain_detail` (the six fields) to the corpus schema and gate it | makes thinness a build failure instead of a review opinion | 2 | 0.5 | Validator fails a zone whose `sustain_detail` is missing any of the six, whose cadence is not one of a closed list, whose `drift_signal` contains no countable noun, or whose `recovery.minutes` exceeds 10. Also fails if `sustain_detail.trigger` is more than 60% identical to `leave_behind.trigger` (the exact defect measured in 2.1). | software-engineer |
| **S2** | Author `sustain_detail` for the 12 video-backed zones | proves the shape and the length model on the only zones with distribution | 2 | 0.75 | 12 zones pass S1. Each is 90 to 130 words. Each names a cadence, an owner, a drift signal that is an object, and a recovery under 10 minutes. None repeats its own `leave_behind.trigger`. | content-editor |
| **S3** | Render `sustain_detail` on the zone page, the app's Sustain card, and the Standards Pack | one authored source, three surfaces, no divergence | 2 | 0.75 | The served zone page shows all six elements. The Sustain card in the Quest shows trigger, cadence, owner and drift signal. `6S-Standards-Pack.html` regenerates with them. All three read from `content.json`; a gate asserts the strings are character-identical across the three. | software-engineer |
| **S4** | Author the remaining 102 | closes the only measurable content gap in the method | 2 | 3.5 | All 114 pass S1. Median Sustain length is at or above the median of the other five passes. Zero zones under 30 words. Cadence named in 114 of 114; owner in 114 of 114; recovery in 114 of 114. Re-run the measurement in 2.1 and publish the new table. | content-editor |
| **S5** | Say so out loud where a household will see it | the drift signal is useless if it is only on a page | 2 | 0.25 | Each of the 12 pilot zones' YouTube descriptions links its zone page anchor `#sustain`. Phil's hand is needed on the description edit; the copy is prepared for him. | product-manager, then **Phil** |

**Total to close the Sustain gap: 5.75 days**, of which 2.25 is the pilot and
the decision point.

**A warning about S4.** 102 zones x roughly 110 words is about 11,000 words that
must be *true of a specific real place*. Generic sustain prose would be worse
than the 28-word version we have, because it would be longer and still empty.
Author it room by room against the zone's own Shine surfaces and hazards. If a
batch starts producing interchangeable sentences, stop and reduce scope to the
40 highest-traffic zones rather than shipping filler (`CLAUDE.md` section 9).

### 2.4 The app's Sustain card must leave something behind

Today the last card of a zone is a card you tap Done on, and nothing survives
the session. `DECK-SYSTEM.md` section 2 sets the test: *it ends in a standard;
something is written, signed, and left in the room.* The app fails that test.

| # | Item | Why | Tier | Days | Acceptance criteria | Owner |
|---|---|---|---|---|---|---|
| **S6** | The Sustain card ends in an artefact | a reset with nothing left in the room regresses, and regression is why 1 person has ever held a zone | 8 (hypothesis: the missing artefact is *a* cause of regression; we cannot observe regression at 1 held zone) | 0.75 | Finishing the Sustain card offers the zone's standard sentence, cadence, owner and drift signal as one printable/copyable card, pre-filled from the corpus, editable in the household's own words, stored in `localStorage` with the rest. "What you are keeping" lists it. No account, no network write, consistent with the page's own privacy claim. | ux-frontend |

---

## 3. The deck line

### 3.1 The contradiction in our own documents, resolved

`BACKLOG-2026-H2.md` says, under what is deliberately not in the backlog: *a
second illustrated deck. The free Entryway deck exists to produce evidence
first. It has not produced any yet.* `DECK-SYSTEM.md` specifies the Kitchen
deck in detail. Both are current and they disagree.

They only disagree about the **pictures**. The Kitchen deck's 72 cards of text
are written, gated against `content.json`, and cost nothing more
(`ops/cardtext/kitchen-deck.json`, verified today: 1 room, 7 zone, 21 friction,
12 root cause, 18 action, 7 standard, 6 event). The expensive and twice-failed
part is the art: `DECK-SYSTEM.md` 6.1 records two Entryway hero images that
passed review while depicting something other than their own card, including a
Key Station card with no key in the picture.

**Resolution: ship the Kitchen deck typeset and unillustrated, free, ungated,
print-at-home. Hold the art until it has downloads.** That tests the thing we
do not know (does the diagnostic loop work in a household's hands) without
spending the thing we know is risky (72 images and a 72-image human review).

### 3.2 What blocks it, measured today

| Blocker | Measurement |
|---|---|
| **65 of 72 Kitchen cards would print as identical dark "Room" cards** | `card_spec.FAMILY` holds the Entryway taxonomy (Micro Zone, Problem, Event, Upgrade, Habit, Skill, Tool, Win, Room). Of the Kitchen types only `ROOM` and `EVENT` resolve; `ZONE`, `FRICTION`, `ROOT CAUSE`, `ACTION` and `STANDARD` fall through `family_of()` to Room ink. Ran it: 65 of 72. |
| **The template is bound to the Entryway corpus** | `ops/build_card_template.py` reads `build/entryway-cardtext.json` at three sites and heroes from `heroes/entryway/`. `ops/build_deck_pdf.py` hardcodes both the corpus path and the output filename. |
| **Five card backs have no layout** | Friction (branching answers), Root Cause (30-second confirmation plus related actions), Action (numbered steps, victory, next card), Standard (write-on rules), Event (held-if / if-it-failed) do not exist in the template. |
| ~~The Entryway deck has three published sizes~~ | **Stale, corrected 2026-09-07, operator.** The "46" claim (`ops/build_printpack.py`/`ops/build_standards.py`) no longer checks out: neither file names 46 anywhere today, consistent with Phil's 2026-08-30 sweep (`DECK-SYSTEM.md` 10.3 was written before that fix landed and was never re-read against the code). What did still check out: `deck.html`'s own title/meta/OG/Twitter tags said 89 with no explanation while `data.js`, `shop.html` and the print-and-play page said 88. Fixed (see K0 below); `build/entryway-cardtext.json`'s 89 (including the Room divider card, per `ops/build_deck_gallery.py`'s own documented rule) and the catalogue's 88 (89 minus that divider) are both correct, deliberate, and now consistently applied. |
| **The `DECK-ENTRY` catalogue tile is a 404** | Carried from `DECK-SYSTEM.md` 10.1, dated 2026-09-04. Points at `assets/img/cards/entryway/...`; the images are at `assets/cards/entryway/`. **Not re-verified against live today** and it must be before it is touched. |

### 3.3 Work items

| # | Item | Why | Tier | Days | Acceptance criteria | Owner |
|---|---|---|---|---|---|---|
| **K0** | ~~Fix the Entryway deck's card count everywhere~~, and re-verify the 404 tile against the live site | we cannot ship a second deck while the first has three sizes and a broken shop image | 2 | 0.5 | **Card-count half done 2026-09-07, operator**, see `BACKLOG-2026-09-07.md` B3. The 404-tile half is unchanged from `DECK-SYSTEM.md` 10.1/`BACKLOG-2026-09-07.md` item 1: the referenced image exists in this repository's own `site/assets/cards/entryway/` build, which is not the same claim as confirming it 200s on the live domain, and this sandbox has no egress to 6s-success.com to check that directly (`CLAUDE.md` 0.3). | content-editor + commerce-manager |
| **K1** | Add the five missing card families to `card_spec.FAMILY`, with colours and glyphs, each checked for contrast | otherwise 65 of 72 cards are the same card | 2 | 0.5 | `family_of()` resolves all seven Kitchen types to distinct families; zero fall through to Room except the room card. Every family's foreground/background contrast is at or above 4.5:1 by the existing `contrast()` helper. | software-engineer |
| **K2** | Give the template, prompt builder and PDF builder a `--deck` parameter | the tooling is a one-deck tool pretending to be a pipeline | 2 | 1.0 | `python ops/build_deck_pdf.py --deck kitchen` produces a PDF from `ops/cardtext/kitchen-deck.json` with no path edits. `--deck entryway` reproduces today's PDF byte-for-byte apart from its timestamp. | software-engineer |
| **K3** | Five new card-back layouts | the diagnostic loop lives on the backs; without them the deck is 72 fronts | 2 | 2.0 | Each renders through `ops/render_cards.py` with no type under the 7pt floor and no overflow, which that tool already enforces. A friction back shows three answers each naming its cause id. An action back shows inputs, 3 to 5 steps, the victory and the next card. A standard back has three write-on lines that survive printing. | ux-frontend + software-engineer |
| **K4** | Build the unillustrated print-at-home Kitchen deck | the whole point | 2 | 1.0 | 72 cards, 8 sheets of fronts and 8 of backs at nine per US Letter, one PDF under 8 MB (the Entryway PDF is 20 sheets and 25 MB, which is a real barrier at a home printer). Prints legibly on a domestic inkjet in greyscale, verified on paper, not on screen. | software-engineer + qa-reviewer |
| **K5** | One page, and one sentence that separates the deck from the packs | today a buyer cannot tell the four artefacts apart and that is our fault | 7 | 0.5 | The deck page, the shop tile and the print-pack page each carry the same two sentences: *The pack tells you the steps for a zone. The deck works out which zone, what is wrong with it, why, and what to do in the next fifteen minutes.* Free, no email, no account, stated plainly. | content-editor + commerce-manager |
| **K6** | Instrument it | `DECK-SYSTEM.md` 7.5 defines the events and none exist | 2 | 0.25 | `deck_full_download` and `deck_page_view` are emitted and readable in the analytics database. Baseline recorded at zero on the day it ships. | analytics-intelligence |

**Total to ship the Kitchen deck: 5.75 days.** Zero new SKUs, zero new Stripe
objects, zero new rows in `data.js`.

### 3.4 How it relates to the printable packs

The confusion is real and measurable: the Whole House Print Pack ($19) is the
684 app cards on paper, a Micro Zone Pack ($4) is 6 of those 684, and the
Entryway deck is free and a different taxonomy entirely. Three of the four are
the same content at three sizes.

The rule from `DECK-SYSTEM.md` section 9 stands and this plan does not soften
it: **no new deck ships unless it retires at least as many SKUs as it adds.**
The Kitchen deck adds zero as a free download. When it is live and downloading,
`commerce-manager` proposes retiring the 7 Kitchen zone packs and `RP-KITCHEN`,
staged, verified against what production is serving rather than against
`data.js`, navigation first and the payment link last. That is not optional
caution: doing it the other way took a live buy button down once already.

### 3.5 Explicitly held

- **The 72 Kitchen images.** $3.24 to $7.20 of API and a 72-image human review.
  Held until the unillustrated deck has a download number. If it has none, the
  art would have decorated something nobody wanted.
- **A physical printed deck.** Stock, pick, pack and returns against 1.7
  visitors a day. `DECK-SYSTEM.md` 1.1 computes contribution near $18.50 a unit,
  meaning 1,077 decks a month for the goal. Specify it, do not list it.
- **The email gate.** Recommended in principle and **hard-blocked**: Listmonk
  returns HTTP 500 and there are 0 subscribers. A gate in front of a broken list
  is a broken button on our best lead magnet.
- **Decks 3 through 20.** One room. The next is earned by evidence from this one.

---

## 4. The web app, rebuilt around micro zones

### 4.1 What is actually happening

- 53 views of `quest.html`, second only to the home page: most arrivals try it
  (`GOALS.md`, measured 2026-09-03).
- **2 sessions have ever finished a card. 1 has ever held a zone.**
- So 51 of 53 arrivals left having done nothing.

Tier 1, verified behaviour, but on n=53. Nothing below should be read as
proven; the diagnosis is tier 8 and labelled.

### 4.2 Why, as best we can tell, labelled as hypothesis

**Tier 8, informed hypothesis, no session recordings and no interviews.** Four
candidates, and the first two are defects we can check without a user:

1. **The first ask is a chore.** The page's one button is *Start at the door, 15
   minutes*. It asks a stranger to go and physically work on their front door
   before they have any evidence this is worth it. The payoff is 15 minutes away
   and the cost is now.
2. **The first card contradicts itself.** 570 of 684 cards print "You can stop
   when" followed by the whole-zone end state (section 1.1). Somebody who does
   the Sort card properly is shown a description they cannot have reached.
3. **The first number they read is 45 to 75 minutes.** `#c-session` prints the
   whole-zone session on card one.
4. **Nothing asks what is wrong.** The app prescribes before it diagnoses, which
   is what `CLAUDE.md` section 6 forbids, and it means the app cannot say
   anything a visitor recognises about their own house in the first screen.

The one thing that is not a hypothesis: the first-run gate hides the progress
dashboard and the three modes until a zone is held, so a visitor who is not
going to press the one button has no other door. That is a defensible design and
its cost is now measurable.

### 4.3 The first thirty seconds, specified

The current opening is: hero, one button, footer. The proposed opening is a
question, because a person recognises a symptom faster than they choose a room.

**0 to 5 seconds. One question, six taps, no room names.**

> **What is annoying you right now?**
> - I can never find my keys
> - The counter is clear on Sunday and gone by Tuesday
> - Nobody puts anything back
> - It gets dirty again the day after I clean it
> - I have to move three things to get the one I want
> - *Show me the house instead*

Drawn from the friction layer (M3), in household words. The sixth option is the
existing start screen, so nobody is trapped.

**5 to 12 seconds. Name the zone and the cause.**

> That is usually the **Landing Zone**, just inside your front door. And it is
> usually a paper problem, not a key problem: the keys move because six sheets
> of undecided paper are holding the surface.

One sentence of why, the zone's reviewed illustration (110 of 114 zones have
one), and the cause named. This is the first moment the app says something about
their house that they did not tell it.

**12 to 20 seconds. One offer with a real number.**

> **Two minutes.** Tip the tray onto the table. Put back only what opens
> something. Leave the paper where it is; that is the next card.
> **Done when:** the tray holds keys and nothing else.

The `first_15` field, at its shortest setting. Not 15 minutes on the first ask.

**20 to 30 seconds. The card.** One instruction, one victory line, one timer
that starts on tap. No pass badge, no "1 of 6", no session length, no offer.

**Only after the first victory** does the app reveal that this was pass one of
six, that this zone has five more, that the room has five zones and the house
has 114. The progress dashboard, the three modes and the print-pack offer stay
hidden exactly as they are today until a zone is held.

### 4.4 Work items

| # | Item | Why | Tier | Days | Acceptance criteria | Owner |
|---|---|---|---|---|---|---|
| **A1** | Per-card victory conditions live in the app | this is item M7 landing on the surface; it fixes a contradiction on 570 cards | 2 | see M7 | On any non-Sustain card, "You can stop when" describes a state reachable by that pass alone. Verified by reading 20 sampled cards across 20 rooms. **See M7 above: the contradiction itself is fixed (Phil, `fa491b1a`, 2026-09-07); the literal acceptance text is not met, since no card is headed "You can stop when" any more, it now reads "The whole zone is done when" plus a clarifying line, which is the same fact told truthfully rather than the specific wording this row asked for.** Verified 2026-09-09, this operator, by reading `renderCard()` in `site/assets/js/quest.js` rather than sampling rendered pages: the relabel and the pass-N-of-6 note are both unconditional code, not per-zone or per-room text, so they apply identically to every card of every zone that carries `done_looks_like`, not just a sampled subset. No card anywhere claims an unreachable stop condition. | software-engineer |
| **A2** | ~~Move the session length off the first card~~ | "45 to 75 minutes" is the first number a first-timer reads | 7 | 0.25 | **Done 2026-09-09, operator.** `site/assets/js/quest.js` now withholds `#c-session` whenever `run.i === 0 && isFirstRun()` (both the symptom-flow's simplified card zero, already hidden before this fix, and the classic "Start at the door" path, which was not). The number returns on the finish screen instead: a new `#f-session` element in `site/quest.html`, populated in `renderFinish()` for any single-zone run once at least one card is done, phrased against whether the zone was just fully held or not. The zone page already stated it (`ops/build_zone_pages.py`'s "One session: X" line), unaffected. Verified in a real headless-Chromium run driving the classic bail-to-house path end to end: `#c-session` empty on card one, correctly showing "15-30 min for the whole zone, six passes" on card two, and `#f-session` reading "The whole zone runs about 15-30 min, all six passes, whenever you want the rest of it." on the finish screen. New `gate_quest_session_placement` in `preflight.py`, `ops/tests/test_gate_quest_session_placement.py` (6 cases, fail-then-pass proved on both halves of the fix). `ops/fingerprint_assets.py` rerun; `site/quest.html`'s own script-tag fingerprint and `site/sw.js` follow. | ux-frontend |
| **A3** | The symptom entry screen | section 4.3, seconds 0 to 12 | 8 | 2.0 | A first-time visitor sees the question, not the button. Six symptoms, each resolving to a zone and a named cause, all sourced from `diagnosis`. Keyboard reachable, 44px targets, and the no-JavaScript path still falls back to today's screen. Depends on M3. | ux-frontend |
| **A4** | The two-minute first action | seconds 12 to 30 | 8 | 0.5 | `first_15` renders at its two-minute setting on the first card of a first run only. The timer starts on tap. Nothing else is on the screen. | ux-frontend |
| **A5** | ~~Instrument the funnel so the next cycle can read it~~ | today we emit `quest-start`, `quest-card-done`, `quest-zone-held`, `quest-first-start`, `quest-offer-shown`. We cannot tell whether people bounce at the ask or at the work. | 2 | 0.5 | **Done 2026-09-09, operator.** `quest-symptom-picked` and `quest-symptom-start` already shipped 2026-09-08; this cycle added the three genuinely missing events to `site/assets/js/quest.js`: `quest-cause-shown` (fires the moment the cause step renders, right after `quest-symptom-picked`, so the ask and the reveal are now two separate moments, not one), `quest-card-abandoned` (pass, elapsed seconds; fires only while a card's timer is running and the tab hides or closes, via `visibilitychange`/`pagehide`, never on a normal Done), and `quest-return` (integer days since the browser's last visit, from a `state.lastSeen` timestamp, session-guarded so a mid-visit reload is not counted as a return). `quest-victory-confirmed` was not added as a separate name: `quest-first-victory` (shipped 2026-09-08) already marks the same fact for the simplified first card, and adding a second event for the identical moment would be the redundancy `CLAUDE.md` section 42 warns against, not a gap. Verified two ways: a new `gate_quest_funnel_events` in `preflight.py` (`ops/tests/test_gate_quest_funnel_events.py`, 8 cases, fail-then-pass proved on all five markers) checks the shipped file statically, and `ops/tests/test_quest_flow.py` was extended to drive a real headless-Chromium session, stub `window.Measure`, click through the symptom flow, and synthetically hide the tab mid-card: `quest-symptom-picked` and `quest-cause-shown` both fire on the pick, and `quest-card-abandoned` fires with the correct pass name on the simulated hide. Not verified: the events actually landing in the live analytics database (no Umami credential in this sandbox; `analytics-intelligence` or Phil can confirm once deployed, same limit every instrumentation change here has shipped under). `ops/fingerprint_assets.py` rerun after the edit (`quest.js` hash `7b7eabf56c` to `d10470e839`, `site/quest.html`, `site/sw.js`, `site/build-id.txt` all follow). | software-engineer + analytics-intelligence |
| **A6** | The Sustain artefact | item S6 | 8 | 0.75 | See S6. | ux-frontend |

**Total app work: 4.0 days** on top of M7's 1.5.

**An honest limit on all of it.** At 1.7 visitors a day this cannot be tested.
The experiment registry computes 1,427 days to significance at current traffic
(`REVENUE-REVIEW-2026-09-04.md` section 5). Every item above must be justified
because it is correct on its merits, and A1, A2 and A5 are the three that meet
that bar without argument: two fix contradictions we can see in the code, and
one makes the next cycle able to see anything at all.

---

## 5. What is downstream of the constraint, and what I would not do yet

The constraint is arrivals: 52 visitors and 144 visits in 30 days, 1.7 a day, 2
search-engine arrivals in the life of the site. Anything that improves the
experience of a visitor who is not arriving does not move the goal.

### 5.1 Serves the constraint. Do now.

| Item | Why it touches arrivals |
|---|---|
| **M4** diagnosis blocks + FAQ entries on the 12 video-backed zone pages | new question-shaped text on pages Googlebot fetched 178 times in 72 hours. Frictions are the query shape; the 29 articles already prove it |
| **M5** kill the 110 identical related-reading blocks | 110 of 114 pages carry a byte-identical block, and every zone endorses every article equally, so no article gets a topical signal from any zone |
| **S5** point the 12 published videos at their zones' Sustain anchors | YouTube is the only channel with any audience, and a description edit is free |
| **K0** fix the deck's three card counts and the 404 shop tile | a broken image on our main free lead magnet, on the only shop the business has |

That is roughly **2.75 days** of work that has a mechanism to reach a stranger.
Everything else in this plan does not, and should be sized accordingly.

### 5.2 Ahead of the constraint, but correct on merit and cheap. Do, small.

- **M1, M2** the vocabulary and schema (1.0 day). Everything else depends on them
  and they cost a day.
- **M3** the 12 pilot zones (1.5 days). Prerequisite for M4, which is the item
  that serves the constraint.
- **M7 / A1** per-card victories (1.5 days). A live contradiction on 570 cards.
- **A2** (0.25), **A5** instrumentation (0.5). Without A5 the next cycle reads
  nothing, and `GOALS.md` decision rule 4 says measure the customer-visible
  thing.
- **S1, S2, S3** the Sustain schema, pilot and rendering (2.0 days). Sustain is
  the S that makes the method a method, and we are shipping it at 28 words.

### 5.3 Would NOT do yet, and why, plainly

1. **S4, the other 102 Sustain passes (3.5 days).** Not until S2's twelve are
   live and the shape has held. Eleven thousand words authored against an
   unproven template is the largest single way to waste this cycle.
2. **M6, diagnosis for the other 102 zones (4.0 days).** Same reason, and it is
   explicitly gated on M4's 21-day read.
3. **The 72 Kitchen card images.** Cheap in dollars, expensive in review, and the
   review has already failed twice on the Entryway deck. Held until downloads
   exist.
4. **A physical deck.** Stock and returns for 1.7 visitors a day.
5. **Decks 3 through 20.** No evidence from deck one, let alone deck two.
6. **Email-gating the deck.** Hard-blocked on Listmonk's HTTP 500. Do not build a
   gate in front of a list that does not accept anybody.
7. **Values, room-function and household-conflict selectors in the app.** The
   most attractive part of the product model and entirely below the constraint.
   A questionnaire in front of a product 51 of 53 people already leave.
8. **Any new SKU, price or bundle.** `REVENUE-REVIEW-2026-09-04.md` section 5:
   159 SKUs for a business with one lifetime sale is a warehouse. Nothing in this
   plan adds one.
9. **Any A/B test.** 1,427 days to significance. Make changes that are correct on
   their merits.
10. **A 115th micro zone, or a seventh S.** The 114 x 6 grid is complete. The gap
    is diagnosis and Sustain depth, not coverage.

### 5.4 Sequence, and the WIP limit

`STATUS.md` section 14 records Workstreams 1 and 2 blocked on Phil and
Workstream 3 open. This plan claims **Workstream 3: the diagnostic layer and the
Sustain pass**, which keeps us at the `CLAUDE.md` section 18 limit of three.

| Phase | Items | Days | Ends when |
|---|---|---|---|
| **1. Defects and foundations** | K0, M1, M2, S1, M7/A1, A2, A5 | 5.0 | The deck has one card count, the shop tile is verified live, the schemas exist and gate, no card shows an unreachable stop condition, and the funnel is readable |
| **2. The pilot twelve** | M3, S2, S3, M4, M5, S5 | 5.0 | Twelve zone pages carry a diagnosis block and a real Sustain pass; no two zone pages share a related-reading set; the videos point at them |
| **3. The Kitchen deck, unillustrated** | K1, K2, K3, K4, K5, K6 | 5.75 | A free 72-card print-at-home diagnostic deck exists, prints on a domestic printer, adds no SKU, and its downloads are counted |
| **4. The first thirty seconds** | A3, A4, A6 | 3.25 | A stranger is asked what is annoying them before being asked to do anything |
| **DECISION POINT** | read M4's 21-day measurement | 0 | `analytics-intelligence` reports whether the 12 pilot pages moved against the other 102 |
| **5. Scale, only if phase 2 read positive** | M6, S4 | 7.5 | All 114 zones diagnose and sustain |

**19 days to the decision point. 26.5 if it says go.**

---

## 6. Honest limits of this plan

- **One customer exists and was a referral.** Nothing here rests on customer
  research, reviews, testimonials or stated demand, because none exists. Every
  claim about why visitors leave is tier 8 and says so.
- **n = 53.** The Quest's behavioural numbers are two completions out of
  fifty-three views. That supports "almost nobody finishes" and supports no
  estimate of how much better any redesign would be.
- **The 178 Googlebot fetches are carried from `GOALS.md` 2026-09-05 and were not
  re-read today.** The SEO argument in 5.1 depends on that crawl continuing; if
  it has stopped, M4 and M5 lose their mechanism and drop below the constraint
  with everything else.
- **The `DECK-ENTRY` 404 is carried from `DECK-SYSTEM.md` 2026-09-04 and was not
  re-verified against production today.** K0 must fetch it before acting.
- **The effort numbers are estimates.** The measurements are not.
- **This plan does not make traffic happen.** Section 5.1 is 2.75 days of work
  with a plausible mechanism, against a constraint that mostly needs Phil's hand
  on 216 unpublished videos and a Search Console verification. If those two
  things happen, everything else in this document is worth more; if they do not,
  the honest sentence from `DECK-SYSTEM.md` 1.2 still applies: this is a bet on
  arrivals succeeding, not an alternative to it.
