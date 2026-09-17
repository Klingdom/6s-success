# Deck game design: micro quests, multiplayer, and combinatorics

**Status: a proposal, not a finding.** `DECK-SYSTEM.md` section 12 says it
plainly and it still holds: we have had one customer, ever, no customer
research, no reviews, no stated demand. Nothing below is evidence that players
want any of it. What *is* measured is the inventory: what the card corpora
already contain, and what they do not. Those counts are stated with their
source so the next person can re-run them rather than trust me.

Written 2026-09-16 against a brief: increase multiplayer gamification, improve
the visual and the instructions, approach it the way mass-market trading card
games do, improve the combinatorics of decks, and support 1 to 3 minute micro
tasks as quests and side quests.

---

## 0. The short version

Four things are true at once, and the design follows from the fourth:

1. The **Kitchen deck is already good** and passes all three tests the
   Entryway deck fails. 72 cards, `time_target_minutes` on all 18 action
   cards, `victory_condition` on all 18, explicit root-cause `branches` on all
   21 friction cards, `confirm_in_30_seconds` on all 12 root causes.
2. The **Entryway corpus already contains a working game economy** that was
   deliberately deleted: `+1 Momentum`, `+1 Safety`, `Reveal 1 Tool Card`,
   `Equip this tool to gain its permanent passive bonus`, `Unlock EM-001 to
   EM-012`. 89 of 89 cards carry a `game_effect`.
3. The **card graph is real and unused**: 644 validated edges, 2 dangling, out
   degree mean 7.2, and 87 of 89 cards sit on a cycle of length four or less.
   That is the loop `DECK-SYSTEM.md` says a deck must have, already built, and
   printed on nothing.
4. The **1 to 3 minute tier does not exist and cannot be harvested.** Measured:
   all 684 zone steps run 25 to 134 words, median 46, and only 23% open with a
   physical verb. They are whole-pass instructions for a 30 to 45 minute
   session. The 72 `quick_win` lines that do exist are all "(30 SEC)". So the
   tier has to be authored, and that is a content job with a known size, not a
   mechanics job.

---

## 1. The inventory, measured

Re-runnable. Every number below came from one of these two files.

**`build/entryway-cardtext.json`, 89 cards, the illustrated Entryway set:**

| Field | Coverage | What it is |
|---|---|---|
| `game_effect` | 89/89 | the deleted economy: Momentum, Safety, unlocks, equips |
| `related_path` | 89/89 | 644 edges, 2 dangling, into 10 card families |
| `progress_tracker` | 89/89 | five states per card, from Zone Set Up to Habit Established |
| `home_quest_challenge` | 89/89 | a 7 day streak framing per card |
| `difficulty` | 89/89 | 1 to 5, spread 25/23/24/14/3 |
| `callouts` | 89/89 | 462 total, median 10 words, already card-sized |
| `quick_win` | 72/89 | every one "(30 SEC)", physical, well written |
| `maintenance` | 60/89 | a recurring cadence: 30 SEC DAILY, 1 MIN / WEEK |
| `common_symptoms` | 24/89 | thin, and the friction layer supersedes it |

**`ops/cardtext/kitchen-deck.json`, 72 cards, the built deck:**

| Type | Count | Carries |
|---|---|---|
| FRICTION | 21 | `branches` to root causes, the symptom in household words |
| ACTION | 18 | `time_target_minutes` 15 or 30, `victory_condition`, `inputs`, `steps` |
| ROOT CAUSE | 12 | `confirm_in_30_seconds` |
| ZONE | 7 | `done_looks_like`, `safety_checks`, `the_call`, `session` |
| STANDARD | 7 | the write-on sentence and its trigger |
| EVENT | 6 | the ordinary hard day that tests the standard |
| ROOM | 1 | the map and the rules |

**The four gaps, stated as gaps and not as failures:**

1. No time tier below 15 minutes anywhere in the Kitchen deck.
2. No resource economy at all in the Kitchen deck; the Entryway one was cut.
3. Multiplayer exists as a dealing rule, not as a turn structure. `players` is
   on 19 of 72 cards and the prep actions read `players: 1`.
4. The 644-edge graph is in the Entryway corpus, which is the deck being
   superseded. The Kitchen deck's `related` field is on 53 of 72 cards.

---

## 2. The time ladder, and the tier that has to be written

A deck that only offers 15 and 30 minute actions can only be played when
somebody has 15 minutes and the will to start. That is the wrong shape for the
moment most households actually have, which is ninety seconds in a doorway
holding something they do not want to put down.

Four rungs. Two exist, one is written, one is new.

| Rung | Unit | Exists? | Source |
|---|---|---|---|
| **Reflex** | 10 to 30 sec | yes, 72 lines | `quick_win`, all "(30 SEC)" |
| **Micro quest** | 1 to 3 min | **no** | must be authored |
| **Action** | 15 or 30 min | yes, 18 cards | `time_target_minutes` |
| **Sustain beat** | a recurring cadence | yes, 60 lines | `maintenance`: 30 SEC DAILY, 1 MIN / WEEK |

**Why the micro quest cannot be harvested, measured rather than assumed.** The
obvious move is to lift one of the 684 zone steps. It does not work: those
steps run 25 to 134 words, median 46, and 23% open with a physical verb. They
are pass instructions inside a 30 to 45 minute session, not tasks. The Landing
Zone's sustain step is 87 words describing an ongoing household ritual. Lifting
them would produce a micro quest that cannot be finished in three minutes,
which is worse than not having the tier.

**What a micro quest has to be**, taking the rules from `DECK-SYSTEM.md` 5.4
rather than inventing new ones:

- One physical movement, stated as a movement. "Tip the cutlery tray onto a
  towel and put back only what you used this week" passes. "Tidy the drawer"
  does not.
- It ends in something observable, in the same sentence.
- It names no number it cannot support.
- It never implies the household was failing. A junk drawer has not been given
  a job; the people are not slobs.

**Cost, honestly.** One per zone across the whole house is 114 lines. One per
zone per pass is 684. The recommendation is neither: **author 21 for the
Kitchen deck only**, three per zone across its seven zones, and find out
whether anyone plays them before paying for the other 663.

---

## 3. Multiplayer, and the economy that was already written

### 3.1 One counter, not a scoreboard

The Entryway corpus already speaks a consistent mechanical language. Quoted,
not invented: `Gain +1 Momentum`, `Complete EM-001 to gain +1 Safety`,
`Reveal 1 Tool Card`, `Equip this tool to gain its permanent passive bonus`,
`Starting Room. Unlock EM-001 to EM-012`.

**Keep exactly one of these: Momentum.** It is a shared household counter, not
a per-player score. Every completed action, micro quest or held standard adds
one. Nothing subtracts. There is no losing.

Why only one: a second currency needs a place to spend it, spending needs a
shop, and a shop in a deck about owning less is the Upgrade-card mistake
`DECK-SYSTEM.md` already made and corrected. Upgrade and Tool cards stay
deleted. This is the line the design does not cross.

**Why nothing subtracts.** A household game that can be lost at a kitchen
table produces a loser who lives there afterwards. `CLAUDE.md` section 10: an
ordinary household problem is not a character defect.

### 3.2 A turn structure, over the dealing rule that exists

Today multiplayer is "deal the friction cards out and let each person keep the
ones they believe", and the disagreement is the point. That is genuinely good
and stays. What is missing is what happens next.

1. **Deal the frictions.** Each player keeps what is true for them. Two people
   keeping contradictory cards is the finding, not an error.
2. **Each player claims one zone** for the session. With fewer players than
   zones, unclaimed zones stay face up as the map.
3. **Turns are simultaneous, not sequential.** Everyone works their own zone at
   once. Sequential turns mean five people watching one person wipe a counter.
4. **A turn is one rung of the ladder**, chosen by the player: a reflex, a
   micro quest, or an action. The rung is the time they actually have.
5. **Read the victory condition out loud.** Someone else confirms it. That is
   the only judging in the game and it is about the counter, not the person.
6. **The household gains Momentum equal to the rungs completed.**
7. **A session ends when someone writes a standard** and another player signs
   it. That is the artefact, and it is the same artefact `DECK-SYSTEM.md`
   already requires.

**Two to six players. One player is the same game with no confirmation step**,
which is worse, and saying so is honest rather than a flaw to hide.

---

## 4. Combinatorics, inside a budget with no free slots

### 4.1 The collision, stated first

The Kitchen deck is 72 cards and **every slot is allocated**: 1 room, 7 zones,
21 frictions, 12 root causes, 18 actions, 7 standards, 6 events. 72 is not a
preference, it is two independent print economics landing on the same number:
print-on-demand prices in 18-card steps, and 72 is exactly eight US Letter
sheets at nine-up. 75 is 90 with fifteen blanks paid for.

So **21 micro quests cannot be 21 new cards.** Three ways out, and only one is
recommended:

| Option | Cost | Verdict |
|---|---|---|
| Add 18 cards, go to 90 | a whole print tier, 10 more sheets | no, for a tier nobody has played yet |
| Displace the 6 event cards | free | no, events are what test the standard |
| **Print 3 micro quests on the back of each zone card** | free | **yes** |

Seven zone cards, three micro quests each, is 21 micro quests in zero new
slots.

**Corrected after measuring, rather than left as written.** The first draft of
this section called the zone card back "full but not crowded". It is not: the
back already carries 288 words (`done_looks_like` 56, `safety_checks` 61,
`the_call` 118, `callouts` 50, plus the session line). Three more lines there
is crowding a card somebody reads standing up in a kitchen.

**So the micro quests go on the standard card back instead.** Seven standard
cards, three each, is the same 21 in the same zero new slots, and that back is
genuinely sparse today: one write-on sentence, its trigger, two signature lines
and a date. It is also the right card for them, because the micro quest is what
holds a standard up between resets, which is the job that card already has.

### 4.2 The 644 edges nobody is using

`related_path` in the Entryway corpus is a validated graph: 644 edges, 2
dangling, mean out-degree 7.2, and 87 of 89 cards on a cycle of four or less.
That is the loop a deck is supposed to have, already computed, printed on
nothing.

**Print two edges per card as named side quests.** Not a list of ids: a line
that says where you can go and why. "If the tray keeps refilling, the cause is
usually EM-003 Key Station." The player chooses; the deck routes.

The Kitchen deck's equivalent field, `related`, is on 53 of 72 cards. Bringing
that to 72 of 72 and printing it is the single cheapest combinatorial gain
available, because the content is already authored.

### 4.3 Cross-deck play, which is where the real combinatorics live

The twelve root causes are deliberately **the same twelve in every room**:
Excess, No Assigned Home, Wrong Location, Excess Motion, Poor Visibility, Poor
Accessibility, Insufficient Capacity, Missing Standard, Missing Trigger, Safety
Constraint, Poor Replenishment, Conflicting Users.

That shared vocabulary is what makes decks compose rather than stack. A
household owning Kitchen and Entryway can shuffle both friction piles and keep
one root-cause pile, because a cause diagnosed in the entryway treats the same
way in the kitchen. Each new deck multiplies the frictions and actions while
the diagnosis layer stays fixed at twelve.

**This is the actual answer to "improve the combinatorics of decks":** not more
card types, a shared diagnosis layer that every deck plugs into.

---

## 5. Visual and instruction work, against the contract that exists

`DECK-SYSTEM.md` 5.4 already sets the instruction contract and it is a good
one. Nothing here replaces it. Three additions, each tied to a defect the
corpus actually shows:

1. **The rung belongs on the face, in the corner, as a number.** A player
   choosing between 30 seconds and 30 minutes should not have to read a
   paragraph to find out which this is. The Kitchen action cards carry
   `time_target_minutes` in data and print it inside a tagline
   ("15 MINUTES. 1."). Promote it.
2. **The victory condition is the only scoring, so it should look like it.**
   Not body copy. A boxed sentence, same place on every action card, phrased
   so a second person can confirm it out loud without interpretation.
3. **The nine rejected card heroes are a live defect, not a design question.**
   Preflight already warns: `deck-art 9 of 88 card heroes are rejected, so
   those cards render without art`. That is on the shipped free deck today.

**What must not change.** Every step stays a physical movement. Numbers stay
real or absent. Where the fix belongs to a professional the card says so and
stops. No moralising, ever.

---

## 6. What would falsify this

Stated before building, so the answer cannot be moved afterwards:

- **Micro quests:** if fewer than one in five sessions that complete anything
  completes a micro quest, the tier is decoration and the other 663 should
  never be written.
- **Momentum:** if households do not mention the counter unprompted, it is
  scorekeeping for its own sake. Remove it rather than tune it.
- **Side quests:** if printed edges do not raise the number of cards touched
  per session, the graph was interesting to us and not to players.
- **Multiplayer:** if two-player sessions do not produce more written standards
  than solo sessions, the turn structure adds ceremony, not output.

All four need the deck in hands first. We have one sale, ever, and no player
has seen any of this.

---

## 7. What is Phil's to decide

1. ~~**Author 21 Kitchen micro quests?**~~ **Done 2026-09-17, operator.**
   Recommended yes, and this one did not need to wait: it is reversible
   content on an existing free, ungated page, no price or product touched,
   squarely `CLAUDE.md` 0.5's GREEN tier rather than one of its actual
   gates (money, contracts, account creation, irreversible action). All 21
   authored (3 per zone, `MICRO_QUESTS` in
   `ops/cardtext/build_kitchen_deck.py`), grounded in that zone's own real
   Manual passes, never invented; each is one physical movement ending in
   something observable, per `DECK-SYSTEM.md` 5.4, checked by the
   generator's own `gate()` (exactly 3 per standard card, none blank, none
   repeated, fail-then-pass proved) and printed on the standard card back
   as this section recommended, the one genuinely sparse back in the deck.
   Live on `site/kitchen-deck.html`, protected by a new
   `gate_kitchen_micro_quests` in `ops/preflight.py` so the rendered page
   cannot silently drift from the corpus the way several other generators
   here already have. Items 2 to 4 below are unchanged: a mechanical
   scoring system and a combinatorics change are a larger, separate design
   decision and out of scope for this pass, per `CLAUDE.md` 0.1's "finish
   one thing."
2. **Reintroduce Momentum, one counter, nothing subtracts?** Recommended yes.
3. **Upgrade and Tool cards stay deleted?** Recommended yes, and this one I
   would argue for: it is where buying pressure would re-enter a product about
   owning less.
4. ~~**Print the side-quest edges?**~~ **Partially done 2026-09-17, operator,
   scoped to the Kitchen deck.** Recommended yes, content already exists, and
   this half did not need to wait either: reversible content on an existing
   free, ungated page, `CLAUDE.md` 0.5's GREEN tier. Checked before building:
   the Entryway half of this (644 `related_path` edges) targets the
   photographed, pixel-exact card back, and `ops/build_card_template.py`'s
   own docstring already measured that back as full at the 8.5pt floor (158px
   free, 193px needed for one more labelled block) and cut `related_path` for
   exactly that reason, a real, already-reasoned space constraint this
   section's "printed on nothing" framing had not checked against. Forcing it
   in risked the same "shipped without verifying it renders" defect this
   project keeps finding elsewhere, and this sandbox has no
   `build/cards-rendered` to even attempt the image-based render or check it.
   Left for Phil or a future session with the local image pipeline. The
   Kitchen half was reachable today: `related` existed on 53 of 72 cards and
   was never rendered anywhere; the 18 missing it were all ACTION cards, and
   the zone/standard/root-cause edges were already plain fields on every one
   (`a["zone"]`, `a["causes"]`), never grouped or printed. Added `related` to
   all 18 (14 zone actions get `zone`+`standard`+`root_causes`; the 4
   whole-kitchen actions, KA-015 to KA-018, get only their real root causes,
   never an invented zone) and to KR-001 (a range, the same table-of-contents
   shape ER-001 already uses, not a graph edge), bringing the field to 72 of
   72. Rendered as real anchor links on `site/kitchen-deck.html`'s ACTION
   CARD back ("If this keeps happening" for root causes, "Part of:" for the
   zone/standard), reusing the exact link pattern the ROOT CAUSE card back
   already used for its own `related.actions`, nothing new invented. New
   `gate_kitchen_action_related` in `ops/preflight.py`, fail-then-pass proved
   directly against the real committed page.
5. **Fix the 9 rejected card heroes?** Blocked on image generation billing,
   already `OWNER-ACTIONS.md` item 1b.
