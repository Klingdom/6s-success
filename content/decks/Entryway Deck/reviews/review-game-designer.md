# Game-Designer Review — Entryway Deck v2 (46 cards)

Reviewer role: published tabletop designer (family + hobby card games, legacy/campaign titles). Card anatomy, table usability, iconography, and "is it actually fun and does it still do the job."

Scope: builds ON the improvement plan and the graphic-artist review (visual system + image usage are theirs; I do not re-do them). I add the three things a designer owns: (1) the card template as a **table object**, (2) real **mechanics** that make this a sellable product line, and (3) **illustration as function**, not decoration.

One-line diagnosis: **the bones are a beautiful reference manual wearing a game's vocabulary.** Card 2 lists five "ways to play," but there is no win state, no tableau, no tokens, no draw/discard, and no reason to finish. The art fixes handled *look*; nothing yet makes it *play*. Below is how to make it a game that still gets the house reset — because the honest version rewards real work, not points.

---

## PART 1 — CARD LAYOUT & ANATOMY (template spec)

### 1.1 The format problem, named
Today each card is **~7.5 × 4.5 in landscape, single-sided** (2 to a letter page). That is a gorgeous lay-flat reference card and a **bad deck**: you cannot shuffle it, fan it, sleeve it in anything standard, hold a hand of it, or lay 30 of them out as a tableau without needing a dining table. It is also single-sided, so every card spends half its surface (the footer + the sparse side panel) on air while the Shine cards overflow. A deck that is played must fit the hand and the table; a reference that is deep must have somewhere to put the depth. **The answer to both is the same: go double-sided and shrink.**

### 1.2 Recommended product format: **Tarot, double-sided (70 × 120 mm)**
- **Why tarot, not poker or A5.** Poker (63×88) is too small for the Shine method + a target image. A5 (148×210) is a booklet page, not a card — you cannot build a 30-card tableau with it. **Tarot is the sweet spot:** shufflable, sleeve-available (standard tarot sleeves exist), fannable from a corner, and a 5×6 tableau of them fits a coffee table. Portrait orientation reads better in-hand and stacks/spreads cleanly.
- **Double-sided split — this is the core template move.** A reference card that is also played has two jobs that fight for the same face. Separate them:
  - **FRONT = the PLAY FACE (at-a-glance).** Everything you need with the card lying in a tableau: which S, which zone, the one action, the done-target, time/effort. No paragraphs.
  - **BACK = the DEEP READ.** The full method (nine-rule Shine, inputs/caddy, inspect-&-flag, the expert tips from the plan). You flip a card up to its back only when you are actually *doing* that step. This is exactly how players use a reference in play — glance at the tableau, flip the one you're on.
- This single decision resolves three of the deck's problems at once: at-a-glance vs deep-read (front vs back), the sparse cards (fronts are *meant* to be sparse and uniform — that is now a feature), and the text-dense Shine cards (the back is a full page).

### 1.3 FRONT template (universal, all 46) — build spec
Portrait 70×120mm, 3mm bleed, 3.5mm corner radius, 4mm safe margin. Reuse the existing palette tokens (`--paper`, `--ink`, per-S colors).

```
┌─[corner index]───────────────── header band (S-color) ──┐
│ ◐S  ▚zone   S-NAME · Zone name                   13/46  │  ← .chd, keep, + two badges
├─────────────────────────────────────────────────────────┤
│                                                         │
│   HERO SLOT (target image / diagram — see Part 3)       │  ← replaces the top of .cmain
│   [ done-looks-like: before→after micro-thumb ]         │
│                                                         │
│   ▸ THE ONE MOVE  (single imperative line, 14px)        │  ← the at-a-glance action
│                                                         │
├──────────────── footer pill (S-color tint) ─────────────┤
│  ⏱15m  ●○○  · target: keys+phone in 1 tray   ·  ●●●○○○  │  ← time/effort + metric + loop-rail
└─────────────────────────────────────────────────────────┘
```
- **Corner index (new, top-left, ~9px).** Like a playing card's rank/suit: the **S-glyph + zone-token** printed small in the corner so a fanned or overlapped spread is readable from the corner alone. This is what makes the "pull one colour" S-pass and any tableau physically work — you sort by corner without spreading everything.
- **Header** = existing `.chd`, keep the S-color bg + title + `num`. Add the two badges the plan already specifies (S-glyph, zone token). Nothing else changes.
- **Hero slot** = one functional image (Part 3), sized to ~45% of the face. This is where the front earns its keep and where the five near-identical types stop feeling identical.
- **The One Move** = a single imperative distilled from the card. e.g. Sort → "Empty it. Nothing back without a verdict." The paragraph that says this now moves to the back.
- **Footer pill** = the plan's ⏱time + ●effort, PLUS a **6-dot loop-rail** (●●●○○○ = "you are on step 3 of 6, Shine") so the card shows its place in the zone's fixed order at a glance. Fills the dead footer, teaches the loop, and lets a player reassemble a shuffled zone in order without reading.

### 1.4 BACK template (activity cards) — build spec
The back is the current `.cbody` content, given room to breathe:
- **Method column** — the numbered steps (Shine's nine-rule rail numbered 1→n, per the graphic artist), each step one line.
- **Side rail** — the fixed per-type unit the plan defines (caddy icon-row on Zones, "home-for-it" diagram on Straighten, red-tag on Sort, 3-clocks on Sustain, inspect-&-flag box on Shine, framed-photo target on Standardize, warning-triangle list on Safety).
- **System cards (1–11)** are reference-only — they can be **single-message double-sided** (front = the summary/scannable version, back = the detail) or printed as **landscape reference cards at 2× tarot** and kept out of the shuffle (they are the rulebook, not the deck — see 2.2).

### 1.5 Killing the 5×(repeat) monotony — a designer's four levers
The graphic artist gave you zone tokens + Safety color; here is how a designer stops repetition from reading as filler and turns it into *rhythm you can play*:
1. **Make repetition a grid, not a list.** Five zones × six S's is a **5×6 matrix**. Once the player sees the tableau as a board they are *filling in*, identical structure becomes reassuring pattern (every card knows its cell) instead of monotony. Repetition is a bug in a list and a feature in a grid.
2. **Zone spine motif.** Give each zone a persistent left-edge spine strip (a 4mm color-accent + zone token repeated down the edge, per the plan). In a fanned hand or a stacked deck, the spine tells zones apart on the table edge — the physical enabler of "grab one zone's seven cards."
3. **Vary the hero, hold the frame.** The frame is identical (good — it is the system); the **hero image is unique per card** (Part 3). Sameness of frame + difference of picture is exactly how a good deck feels consistent without feeling repetitive.
4. **Numbered loop-rail** (1.3) makes the six S-cards of a zone a *sequence with position*, not six interchangeable siblings.

### 1.6 Print / cut / sleeve practicality
- 46 tarot cards = a healthy but not bloated deck. Split the **11 system/reference cards** from the **35 play cards** (5 Zone + 30 S-activity) so the shuffle-and-play deck is a clean 35 and the reference/rulebook cards live in a front-of-box "guide" band.
- Standard tarot bleed/safe/round-corner as above; **backs are shared-artwork per S** at the system level but **unique deep-read per card** — so no "which way up / which card" confusion, and the corner index disambiguates in a spread.
- Sell per room in a **tuck box or two-piece box** with a die-cut window showing the cover hero. The tracker mat (2.5) is the box insert or a separate pad.

---

## PART 2 — GAME MECHANICS (make it a real, replayable product line)

Design rule I will not break: **the game rewards real completion, verified by photo — never abstract points.** If a mechanic could be "won" without the room actually being reset, it is cut. This is what keeps it honest and is also, not coincidentally, what makes a chore-game trustworthy enough to buy.

### 2.1 The core loop = fill the board
The 30 S-activity cards + 5 Zone cards form a **5×6 tableau (the board)**. This is the missing win state.
- **Setup:** lay the 5 Zone cards down the left as row headers; leave six empty columns (Sort → Straighten → Shine → Safety → Standardize → Sustain). Either physically place the 30 cards face-down in the grid, or use the printed **Tracker Mat** (2.5) with 30 slots.
- **Play a cell:** take the card, flip to its deep-read back, do the real task, then set it **face-up (play face) in its cell** = that cell is *cleared*. The board visibly fills. Filling the board *is* the progress bar, and it maps 1:1 to real work.
- **Win a zone:** all six cells of a row cleared **and** the row passes its 6S Audit (2.4). Earn the **Zone crest** (stand the Zone card up as a trophy / stamp the mat).
- **Win the room:** all five zones cleared **and** the After photo matches the Standard photo (Card 10). That is the honest win condition — you win when the entryway is actually reset.

### 2.2 Onboarding (already half-right — finish it)
- Card 1 already says "Start here: do the Landing Spot, ~20 min." Keep it as the **tutorial**: one zone, six steps, one before/after pair. That is a perfect 20-minute first session that teaches the whole loop on the room's highest-leverage square foot.
- Promote the 11 system cards to a **"Read-Me / Rules" band** at the front of the box: Cover → How to Play → 6S Legend (the master key) → Kit → the four "night" cards (Purpose/Values/Before/Audit) as pre-game setup, and Signature/Rhythm as end-of-game. New players read six cards, then play. Do not shuffle the rulebook into the draw pile.

### 2.3 The five "modes," rebuilt as actual mechanics
Card 2 currently *names* modes; give each a real procedure:
- **Full Reset (campaign):** clear the whole 5×6 board over one or several sessions. The flagship solo/household mode.
- **S-Pass (draft one color):** pull all five cards of one S (by corner index) and sweep the room in that lens — a 15-minute themed run. Mechanic: one column of the board at a time.
- **One Zone (a short session):** pull one zone's seven cards by the spine strip; a self-contained 20–30 min game with its own crest.
- **Daily Draw (habit engine):** the 30 activity cards (or a Sustain-only subset) become a **draw pile**; draw 1 = today's task; done → **discard**. Reshuffle when the pile empties. This is the deck's replayability spine — the room decays, you keep drawing. Track streaks on the mat (2.5).
- **Family Challenge:** two honest variants —
  - *Race (competitive):* deal the five zones among players; first to clear a zone wins it — **but a zone only scores if it passes its Audit** (the quality gate that stops rushing/cheating and is the reason a chore-race still cleans the house).
  - *Relay (cooperative):* everyone works one zone together, each person owns one S (one Sorts, one Straightens…), beat a shared timer. Great for kids.

### 2.4 Scoring & win — reuse what's already there
- **The 6S Audit (Card 8) IS the scorecard.** 0–2 per S = /12. Do not invent a second scoring system. Score the room **before** (baseline) and **after** (result); the **delta** is your score and your bragging number. Under 8/12 → the deck already tells you to re-run the lowest S; that is a built-in difficulty valve.
- **Anchor to the Black Belt's three counted metrics** (from the plan): **seconds-to-launch (<60, zero hunting), items on any surface (≤3), empty hooks (=2).** Capture them on Before (7) and After (10). These are the pass/fail win-check that keeps "did we really win" objective.
- **Crests & the whole-house meta-game.** Because you sell a deck per room, the product line wants a spine: a **House Passport / wall tracker** that stamps each room as it is reset and audited. Reset all rooms in a season = a **House crest**. This is the campaign/legacy hook that turns single decks into a collectible, re-runnable system — and gives you a natural expansion SKU (Passport + token pack).

### 2.5 How the deck physically works (draw pile · discard · tableau · tracker)
- **Tableau:** the 5×6 board (2.1), on the table or on the mat.
- **Draw pile / discard:** used in Daily Draw and Family Race; corner index lets you re-sort a shuffled deck back into zone/S order fast.
- **Tracker Mat (new component — ship it).** A fold-out mat or a **tear-off pad** (consumable = repeat play + a refill SKU) carrying: the 5×6 grid, before/after photo pockets, the Audit scoresheet, the three metrics, and a 30-day Sustain streak calendar. This offloads "tracker" from the cards (so the cards stay clean) and makes the win state tangible. A pad you tear a fresh sheet from each reset is the honest, replayable heart of the product.
- **Token set (new — cheap, high-impact).** A small punchboard: **red-tag tokens** (place on anything failing Sort — Card 13's red-tag concept becomes a physical object), **hazard triangles** (for the Safety Blitz hunt), **done-checks** (mark cleared cells if not flipping cards), and a **"2 empty hooks" gauge** chip. Tokens turn abstract instructions into moves you make with your hands — the difference between reading a manual and playing a game.

### 2.6 Difficulty & replayability (the honest engine)
- **The room decays — that is the replay.** Sustain (daily/weekly/seasonal) is not filler; it is the difficulty timer. The board re-dirties, you re-run. Seasonal swap (coats/shoes by weather) is a scheduled full re-play with real stakes.
- **Modifiers / challenge cards:** time-attack, "no-hunt" run (fail if anyone hunts >10s), "solo speed" vs your own best delta. A few challenge cards per deck add variety cheaply.
- **Kid mode is latent and free:** the **Safety Blitz (Card 9) is already a scavenger hunt** ("find five hazards"). Give kids the hazard-triangle tokens and let them hunt — that is a genuinely fun 2-minute family game that also does safety. Lean into it.

---

## PART 3 — ILLUSTRATIONS THAT SERVE PLAY (function, not decoration)

The test for every image: **does it change what the player does, or is it wallpaper?** Each card TYPE has a different functional job for its art. The graphic artist mapped which plate goes where; I specify what the art must *do* and what medium (photo / icon / diagram) that job demands.

### 3.1 What each card TYPE's art must DO
| Card type | Functional job of the art | Right medium | Asset |
|---|---|---|---|
| **Cover (1)** | Sell + orient in one look; show the payoff | Illustration (before/after) | plate **31-01** full-bleed |
| **Zone (12/19/26/33/40)** | **Show the win-state you play toward** (the "reset looks like" target) + carry the zone token | Photoreal standard, framed | **31-05/06/07/08**; token mined from **31-02** |
| **Sort (13/20/27/34/41)** | Name the *move* (place a red-tag) | Icon / token | red date-tag glyph = the physical **red-tag token** |
| **Straighten (14/21/28/35/42)** | Show **where each thing goes** (spatial map) | Diagram (SVG) | "a home for it" mini-diagram (per plan) |
| **Shine (15/22/29/36/43)** | Drive **order of operations** (top→bottom, don't skip) | Diagram rail + photo on back | numbered rail; **31-09** framed on back |
| **Safety (16/23/30/37/44)** | **Be the hunt board** — show what a hazard looks like so you can spot yours | Photo w/ warning callouts | **31-10** model; hazard-triangle tokens |
| **Standardize (17/24/31/38/45)** | Hold **the player's own after-photo** as the target | Photo pocket (player's image) + frame glyph | framed-photo/target glyph + real photo slot |
| **Sustain (18/25/32/39/46)** | Show the **habit dial** (daily/weekly/seasonal) | Icon | 3-clocks chip stack (per plan) |

The two most important functional images in the whole deck are ones **the player takes themselves**: the **Before** (7) and the **After/Standard** (10, and each zone's Standardize). The card is a *frame* for the player's photo. No stock image beats "your own doorway, then and now" for motivation or as an objective win-check — so design those cards as photo holders, not illustrated cards.

### 3.2 The icon / token system (one language across card, token, and tracker)
Define one vocabulary and reuse it everywhere — on the card face, on the punchboard tokens, and on the tracker mat. That triple-reuse is what makes a game feel like a *system*:
- **6 S-glyphs:** magnifier (Sort) · house (Straighten) · sparkle (Shine) · **shield (Safety)** · camera (Standardize) · loop-arrow (Sustain). These are the corner index, the header badge, and the tracker column heads.
- **5 zone tokens:** keys · coat · shoe · bench · door (from 31-02). Corner index, spine strip, tracker row heads.
- **Play tokens (punchboard):** red-tag (Sort), hazard-triangle (Safety), done-check (cell cleared), 2-empty-hooks gauge.
- **Safety must not vanish** (the graphic artist's flag, and it is load-bearing for play): the shield glyph + the honey-amber alert tone (#DDA63A) must be unmistakable, because Safety is the one S with a token-driven mini-game hanging off it. If Safety reads as "just another grey," the hunt loses its anchor.

### 3.3 Photo vs icon vs diagram — the rule
- **Photo (framed photoreal plate or the player's own):** for **recognition** — target/standard states and real defects. You use a photo when the player must match reality to an image (win-state, "does my hook look like *that* loose one"). Frame all photoreal plates in one consistent inset treatment so they don't clash with the flat SVGs (per the graphic artist).
- **Icon:** for **speed** — navigation (corner index, badges), tokens, and the habit dial. Anything scanned in under a second.
- **Diagram (SVG):** for **relationships and order** — "where it goes" (Straighten) and "in what sequence" (Shine rail). You use a diagram when position or order is the information.

### 3.4 Canon / reject (inherited, and why it matters for play)
Respect the graphic artist's rejects — and note two are *mechanically* dangerous, not just off-brand: **31-13 / 31-14** bake a **wrong five-phase model** that contradicts the six-S loop the whole board is built on — putting them in would break the rules the tableau teaches. **31-11 (friction meter)** is the retired scoring device; it would compete with the Audit-as-scorecard (2.4) and confuse the win condition. **31-12 / 31-15** are the wrong room. Reject all five; use the 10 approved plates on the cards above.

---

## SUMMARY (for the panel)

1. **Format:** the deck is a great lay-flat reference and a bad shuffle-and-play deck. Go **tarot-size, double-sided** — FRONT = at-a-glance play face (corner index, one hero image, one imperative, time/effort + a 6-dot loop-rail), BACK = the deep-read method. This fixes at-a-glance-vs-deep-read, the sparse cards, and the dense Shine cards in one move.
2. **Anti-repetition is structural, not cosmetic:** frame the five identical S-runs as a **5×6 board the player fills in** — repetition becomes reassuring pattern; hold the frame identical and make the hero image + zone spine + loop-position unique per card.
3. **Mechanics — the real gap:** the deck names five modes but has no win state. Add a **5×6 tableau you clear cell-by-cell with real tasks**, win zones via the existing **6S Audit as the scorecard** (before/after delta + the three counted metrics), and win the room when the **After photo matches the Standard**. Honest by construction — you cannot "win" a dirty room.
4. **Ship two new components:** a **Tracker Mat / tear-off pad** (grid + photo pockets + audit + streak calendar; a natural refill SKU) and a **token punchboard** (red-tag, hazard-triangle, done-check, empty-hook gauge) that turn instructions into physical moves.
5. **Product line:** per-room decks + a **House Passport / wall tracker** that stamps each reset room = the campaign/legacy spine and the expansion SKU; Daily-Draw is the replay engine as the room decays.
6. **Illustration = function:** Zone art shows the **win-state target**; Safety art is a **hazard-hunt board** (the Safety Blitz is already a kids' scavenger game — lean in); Standardize/Before/After are **frames for the player's own photos** (the best functional image on any card). Photo for recognition, icon for speed, diagram for order. Keep the 10 approved plates; the 5 rejects include two that would break the six-S rules the board teaches.
