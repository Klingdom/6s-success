# Game-Layer Review — Entryway Deck (6S Success: Home Edition)

**Reviewer role:** Tabletop game designer, focused on mechanics, economy, and card-to-card system coherence.
**Cards examined (fronts + backs):** EM-001, EM-002, EM-005, EM-011, EM-012 (Micro Zone / green); EP-004, EP-010, EP-012 (Problem / red); ET-001, ET-002, ET-005, ET-012 (Tool / green).
**Date:** 2026-07-30

---

## Executive summary

As *reference cards* these are excellent — clean, consistent, information-dense, and genuinely useful for organizing an entryway. As a *game*, the layer is currently **decorative, not mechanical**. Every card names currencies ("+1 Safety," "+1 Momentum," "Permanent Bonus"), a quest, a progress tracker, and a nine-slot "Related Card Path," but there is no turn structure, no win condition, no resource sink, and no rules card that tells anyone what any of it does or how a round is played. The pieces of a good engine-builder / legacy-style co-op are all *pictured* here; none of them are *wired together*.

Compounding this, the cross-reference graph — the one system that is doing structural work — is riddled with copy-paste errors (self-referencing links, wrong prefixes, a Tool where a Zone should be). Because the "Related Card Path" is the connective tissue of the whole deck, these bugs are high-impact: they will send a player to the wrong card or a card that doesn't exist.

The good news: the underlying real-world loop (audit a zone → fix it → sustain it 7 days) is already a proven game loop. It just needs to be *named as the rules* instead of scattered across nine mini-panels.

---

## 1. Resource / economy

### What's on the cards
| Currency | Where it appears | Amount |
|---|---|---|
| **Safety** | EM-001 only | +1 |
| **Momentum** | Nearly every card (EM, EP, ET) | +1 (EM-012 gives +2) |
| **Permanent Bonus** ("+1 Permanent Key Bonus," "+1 Permanent Coat Bonus") | All Tool (ET) cards | +1, star-rated 3/3 |
| **Reveal / Draw** ("Reveal 1 Tool Card," "Reveal 1 Problem Card," "Draw 2 Habit Cards") | EM and EP cards | 1–2 |
| **Family Friendly** (5-star) | Micro Zone cards | rating, not spendable |

### Findings
- **No sink, no threshold, no win condition.** Momentum is granted constantly and spent *never*. A currency you only ever accumulate and never spend or race isn't an economy — it's a score with no target. Nothing on any card says "at N Momentum you win / unlock / trigger X."
- **"Safety" is orphaned.** It appears on exactly one card (EM-001) and nowhere else. It reads as the first of the six S's (Safety, Sort, Set, Shine, Standardize, Sustain), which strongly implies a **six-track resource system** — but the other five S's never appear as currencies on any card, and no card consumes Safety. Either commit to six S-tracks or drop the term. Right now it's a promise the deck doesn't keep.
- **"Permanent Bonus" is undefined.** Every Tool shows a 3-star "PERMANENT BONUS" and a "+1 Permanent [X] Bonus" badge, but nothing states what a Permanent Bonus *does* mechanically (a passive +1 to what? a re-roll? a discount on future resets?). And the sub-type is inconsistent: **ET-005 Entry Bench and ET-012 Charging Station both grant a "+1 Permanent KEY Bonus"** — a bench and a charger giving a *key* bonus is a clear copy-paste from ET-001 Key Bowl. A bench bonus should be a shoe/seat bonus; a charger bonus a device bonus.
- **"Reveal / Draw" implies a deck engine that isn't defined.** "Reveal 1 Tool Card," "Draw 2 Habit Cards," "Equip Tools to All Zones," "Tools may be equipped to this Micro Zone" all describe a hand-management / equip mechanic. There is no rule for a draw pile, a hand size, an equip slot, or what an equipped Tool changes. This is the most promising latent mechanic in the whole deck and it's completely unspecified.

### Recommendation — make it a real engine
Pick **one** primary currency and give it a sink and a target:
- **Momentum** = the engine currency. You earn it by completing zones/solving problems. You **spend** it to Equip Tools (each Tool costs Momentum to play into a Zone) and to trigger Events.
- **The six S's** = a **completion track**, not a floating currency. Each Zone completed advances the relevant S. Filling all six S's for the Entryway = the deck's win.
- **Permanent Bonus** = a defined passive: an equipped Tool permanently reduces that Zone's *Reset cost* (e.g., a Zone with the Key Bowl equipped resets for 1 fewer Momentum / stays "held" without a daily check). This makes Tools an actual engine-building decision instead of a badge.

---

## 2. Card-type system & the "Related Card Path"

### The type graph is sensible in principle
EM (Zone) ← EP (Problem afflicting a zone) ← ET (Tool that fixes it), plus the referenced EH (Habit), ES (Skill), EU (Upgrade), EW (Win), EE (Event), EX (Expert). That's a teachable, logical family: **Zone has a Problem → Tool solves Problem → Habit sustains it → Win rewards it.** Good bones.

### But the "Related Card Path" is mostly filler *and* buggy
Every card lists all nine types with a target code. The intent (a navigable web) is great, but in practice:
1. **It's uniform to the point of being noise.** Most cards just point to the same-numbered card in every family (EM-005 → EP-005, ET-005, EH-005, ES-005…). That pattern is clearly auto-generated, not authored, and it can't all be meaningful — e.g., is there really a Skill ES-005 and an Expert EX-005 that specifically pair with the Shoe Zone? If those target cards don't exist, every one of these is a dead link.
2. **Confirmed cross-reference bugs (high impact):**
   - **ET-001 Key Bowl → Micro Zones "to EN-001"** — `EN` is not a family prefix. Should be **EM-001**.
   - **ET-002, ET-005, ET-012 → Micro Zones "to ET-001"** — the *Micro Zones* slot points to a **Tool** (ET-001), not a Zone. Wrong family entirely.
   - **ET-005 Entry Bench → Wins "to IW-001"** — `IW` isn't a family; should be **EW-001**.
   - **ET-012 Charging Station** has a **wholesale mangled path**: Tools "to **ID**-001," Habits "to **IH**-001," Skills "to **IS**-001," Upgrades "to **IU**-001," Wins "to **IW**-001," Events "to **IE**-001," and **Next Card "ID-001 Key Bowl."** The `E` prefix was replaced with `I` across the board, and the Next Card even reuses the Key Bowl name/art. This card's entire navigation layer is broken.
   - **EP-010 Sports Gear → Problems "to EP-010"** — self-reference (a card pointing to itself as its related Problem).
   - **EP-012 Morning Rush → Problems "to EP-012"** — self-reference again.
   - **EM-011 Guest Welcome → Events "EVERTS to EE-012"** — "EVERTS" typo for "EVENTS."
3. **The GAME EFFECT "solve" links are internally inconsistent:**
   - EP-004 Backpack: "Complete Backpack Station (**EM-007**) to solve." Fine — points to a Zone.
   - EP-010 Sports Gear: "Complete Sports Gear Station (**EM-010**)." Fine.
   - **EP-012 Morning Rush: "Complete Morning Rush (EP-012) to solve this problem."** — tells you to complete the problem to solve the problem. Circular; almost certainly should point to a Tool/Zone (e.g., the Morning Command Center).
   - Tool cards say "**Play [Tool] (ET-xxx) to solve this problem**" — but which problem? A Tool card doesn't name the Problem it solves in the GAME EFFECT, so the ET→EP link is asserted but not identified.

### Recommendation
- **Cut the nine-slot path down to the 2–3 links that are real and load-bearing** per card: for a Zone, its top Problem and the Tool that fixes it; for a Problem, the Zone it lives in and the Tool that solves it; for a Tool, the Problem it kills and the Zone it upgrades. A short, *correct* path teaches the graph; a long, wrong one erodes trust.
- **Make links bidirectional and verified.** If EP-004 says "solved by EM-007," then EM-007 must exist and reference EP-004 back. Build a link table and validate it (no self-references, no cross-family mismatches, no non-existent prefixes) before print.
- **Only reference families that ship in the box.** If EH/ES/EU/EW/EE/EX cards aren't in this deck, either include a few or drop those slots — don't print links to cards that don't exist.

---

## 3. Difficulty vs Friction Level vs Permanent Bonus stars

These are **three different labels sharing one 5-star widget**, and they do **not** mean the same thing:
- **Micro Zone → "DIFFICULTY"** (EM-001/002/005 = 1★, EM-011/012 = 3★). Reads as effort-to-complete.
- **Problem → "FRICTION LEVEL"** (EP-004 = 5★, EP-010/012 = 4★). Reads as how much pain the problem causes.
- **Tool → "PERMANENT BONUS"** (all = 3★). Reads as how strong the upgrade is — but it's **always 3**, so it carries zero information.

Mechanically, **none of them do anything** right now — no card says a 5★ Friction Problem is harder to solve, costs more, or scores more than a 1★ one. Three problems:
1. Using the same visual (stars) for three unrelated axes will make players assume they're comparable ("is a 3★ Zone as hard as a 3★ Friction problem?"). They aren't.
2. The Tool star is a constant, which is a wasted design lever — Tools should vary in power.
3. Nothing converts stars into game value.

### Recommendation
- **Keep the three axes but differentiate the icons and tie each to a number that matters:**
  - Zone **Difficulty** → the **Momentum cost / time** to complete it (1★ = cheap/fast, drives play order).
  - Problem **Friction** → the **Momentum reward** for solving it *and* the **penalty per turn** it inflicts while unsolved (5★ Backpack is urgent — it bleeds you until fixed). This instantly makes Friction a real pressure.
  - Tool **Bonus** → the **strength of the Permanent Bonus** (vary it 1–3★; a 1★ tool is a small passive, a 3★ tool is a game-changer worth saving Momentum for).
- Use a distinct icon per axis (e.g., a difficulty gauge, a friction/heat bar, a power crystal) so the three scales are visually un-confusable.

---

## 4. Does the game reinforce the real behavior, or can you "win" without doing the work?

**Right now you can 100% game it.** Every scoring hook is self-attested: "7-Day Challenge Complete," "Habit Established," "Solution Implemented" are checkboxes a player ticks. Nothing anchors a point to observable reality, so a player can flip cards and check boxes without ever touching the entryway. The "GAME EFFECT" and "PROGRESS TRACKER" reward *card manipulation*, not *room state*.

This is the single biggest gap for a product whose whole value is the real reset.

### Recommendation — bind scoring to the 6S audit loop
- **Before/After gate.** Adopt the book's audit-baseline idea: to claim a Zone, you take a 10-second "before" (photo or the card's own symptom checklist scored 0–5), do the reset, then score "after." **Points = the delta**, not a checkbox. You literally cannot score without a state change to measure. (Note: the book's memory flags that the "audit-baseline promise" was never paid off in Ch 5 — this deck is the natural place to finally cash it in.)
- **Physical proof-of-completion.** The Home Quest 7-day streak should be tracked on the card with a **date-stamped punch/checkbox per day**, ideally verified by a second household member (co-op accountability), not a single "done" tick.
- **Sustain decay.** A completed Zone that isn't reset **decays** (loses its Permanent Bonus / flips back to "problem" side) after N missed days. This mirrors real entropy and is the mechanic that forces ongoing real behavior — the streak isn't a one-and-done score, it's a maintained state. This is what turns "win once" into a legacy/campaign loop.
- **Common Symptoms as the audit rubric.** Each card already lists 8 "Common Symptoms." Reuse them directly: count how many are present before/after — that's your objective, un-gameable score, and it costs no new content.

---

## 5. Onboarding — could a family learn to play from the cards alone?

**No.** There is no rules card, no turn order, no setup, no win condition, no starting hand, and no explanation of what any currency does. A family would correctly use these as *tip cards* and never realize a game exists. The game vocabulary (Momentum, Reveal, Equip, Permanent Bonus, Unlock) appears only as flavor with no referent.

Also confusing: **EM-011 Guest Welcome is labeled "Starting Room" / "Unlock EM-001 – EM-012"** in its GAME EFFECT, while **EM-001 Front Door says it "unlocks the rest of the entryway zones."** Two different cards both claim to be the start. A new player can't tell where to begin.

### Recommendation — add the missing scaffolding
1. **A Rules Card (or small foldout):** 6-line core loop, turn structure, setup, and win condition. Non-negotiable for a playable product.
2. **A one-page glossary** defining every currency and keyword (Momentum, Equip, Reveal, Permanent Bonus, Streak, Decay). Put icon = meaning.
3. **Define one canonical start.** Make **EM-001 Front Door** the single starting card (it already has "unlocks the rest" and a 1★ difficulty). Remove "Starting Room" from EM-011.
4. **A starting hand / setup:** e.g., "Lay out all EM Zone cards problem-side-up; draw your first Problem; take 0 Momentum." Concrete first turn.
5. **Modes card:** Solo, Family Co-op, and a light Competitive variant (below), each in 3 lines.

---

## 6. Fun & replay

**Strong latent hooks already on the cards:** the 7-day Home Quest streaks, the Zone→Problem→Tool chain (natural engine-building), Events (EE) and Experts (EX) as wildcard/help cards, and the room-to-room expansion (EM-012 links to **ER-002 Living Room** — a cross-deck campaign is clearly intended).

**Recommendations:**
- **Lead with co-op.** This is a household activity; a family *vs. the mess* co-op (beat the Entryway before Friction penalties overwhelm you) fits the theme far better than player-vs-player, and it drives real cooperation on the actual chore.
- **Use Events (EE) as the pressure/randomizer** the loop currently lacks: "Unexpected Guests," "Rainy Week," "Sports Season" spike Friction on relevant Zones and force reprioritization. Right now the game has no opposition; Events are the ready-made antagonist.
- **Experts (EX) as one-shot help / hints** — spend Momentum to pull an Expert for a bonus reset or to negate an Event. Gives Momentum a sink and makes the tip content into a resource.
- **Keep the streaks, but make them the campaign spine**, not a per-card afterthought: a household "season" = fill every Zone's streak once; Decay is the replay driver.
- **Light competitive variant:** in a bigger household, race to Habit-Established on your assigned Zones; ties broken by before/after delta. Optional, secondary to co-op.
- **Cut:** the uniform nine-slot Related Path (replace with 2–3 real links), the always-3★ Tool rating (vary it), and the redundant twin "starting" cards.

---

## DECK-WIDE

### Core loop & win condition — as it SHOULD be
*On your turn, face the most urgent **Problem** afflicting an Entryway **Zone** (its Friction rating both rewards you for solving it and penalizes the household each round it festers). Spend **Momentum** to **equip a Tool** that solves it, then physically do the reset and score the **before/after delta** using the card's own Common-Symptoms checklist — you cannot score without changing the real room. Solving Zones advances the six **S** tracks and earns Momentum, which you reinvest in stronger Tools (each granting a defined **Permanent Bonus** that lowers that Zone's upkeep) and in **Experts** to blunt **Event** cards that spike Friction. A Zone you stop maintaining **decays**, so the household must keep resetting to hold its gains. **You win the Entryway when all six S tracks are filled and every Zone holds a verified 7-day streak** — then the deck hands off to the next room (Living Room, ER-002) for the campaign.*

### Top 8 mechanic fixes, ranked by impact
1. **Write a Rules Card + glossary and define ONE start (EM-001).** Without turn order, win condition, and keyword definitions, there is no game. Remove the duplicate "Starting Room" claim on EM-011. *(Blocks everything.)*
2. **Bind scoring to a before/after audit, not checkboxes.** Score the delta of the Common-Symptoms list per Zone so the game can't be won without doing the real reset. *(This is the product's whole point.)*
3. **Give Momentum a sink and a target.** Spend it to equip Tools and pull Experts; set an explicit win threshold (six S-tracks filled). Turn a floating score into an economy.
4. **Fix the cross-reference bugs and shrink the Related Card Path to 2–3 verified links.** Correct EN-001→EM-001, the ET "Micro Zones→ET-001" mismatches, ET-012's whole `I`-prefix path + wrong Next Card, the EP-010/EP-012 self-references, and "EVERTS." Build and validate a link table. *(High impact: the graph is the connective tissue.)*
5. **Make the three star scales mechanical and visually distinct.** Zone Difficulty = completion cost; Problem Friction = reward + per-turn penalty; Tool Bonus = variable power (stop printing a constant 3★).
6. **Add Decay / sustain pressure.** Uncompleted-maintenance Zones lose their Permanent Bonus and flip back to Problem side — this creates the ongoing loop and the campaign's replay engine.
7. **Turn Events (EE) into the co-op antagonist and Experts (EX) into the Momentum sink for help.** Gives the game opposition and tension it currently lacks, and monetizes the tip content as resources.
8. **Fix the Tool bonus semantics.** ET-005 and ET-012 must not grant a "Key Bonus" — bind each Permanent Bonus to its own object (shoe/seat, device) and define what a Permanent Bonus actually does.

---

### Appendix — per-card game-data log (as printed)
- **EM-001 Front Door** — Difficulty 1★. Effect: "Complete EM-001 to gain +1 Safety. Card unlocks the rest of the entryway zones." Path all `…-001/002` family, valid. *Only card that grants Safety; only card with the distinct "Zone Set Up / Issue-Free Week" tracker.*
- **EM-002 Landing Zone** — Difficulty 1★. Effect: "Starting EM-002–EM-004, Gain +1 Momentum, Reveal 1 Problem Card, Tools may be equipped." Path valid.
- **EM-005 Shoe Zone** — Difficulty 1★. Effect: "Starting EM-005–EM-007, +1 Momentum, Reveal 1 Problem Card." Path valid. *(Front has a rendering glitch in the bottom-left checklist/QR block — cosmetic.)*
- **EM-011 Guest Welcome** — Difficulty 3★. Effect: "**Starting Room**, Unlock EM-001–EM-012, +1 Momentum, Reveal 1 Problem." Path: "**EVERTS** to EE-012" typo. *Conflicts with EM-001 as the start.*
- **EM-012 Departure Checklist** — Difficulty 3★. Effect: "Completes the Entryway Set. Unlocked: Full Entryway Bonus. **+2 Momentum. Draw 2 Habit Cards. Equip Tools to All Zones.**" Next Card **ER-002 Living Room** (cross-deck). *Best-articulated game effect in the deck; good template.*
- **EP-004 Backpack Explosion** — Friction 5★. Effect: "Complete Backpack Station (EM-007) to solve. +1 Momentum, Reveal 1 Tool Card." Solve-link valid.
- **EP-010 Sports Gear Explosion** — Friction 4★. Effect: "Complete Sports Gear Station (EM-010)…" Path bug: **Problems → EP-010 (self)**.
- **EP-012 Morning Rush** — Friction 4★. Effect bug: "**Complete Morning Rush (EP-012) to solve this problem**" (circular). Path bug: Problems → EP-012 (self).
- **ET-001 Key Bowl** — Permanent Bonus 3★, "+1 Permanent Key Bonus." Path bug: **Micro Zones → EN-001** (should be EM-001).
- **ET-002 Wall Hooks** — Permanent Bonus 3★, "+1 Permanent Coat Bonus" (correct sub-type). Path bug: **Micro Zones → ET-001** (Tool, not Zone).
- **ET-005 Entry Bench** — Permanent Bonus 3★, badge wrongly says "+1 Permanent **Key** Bonus." Path bugs: Micro Zones → ET-001; **Wins → IW-001** (should be EW-001).
- **ET-012 Charging Station** — Permanent Bonus 3★, badge wrongly "+1 Permanent **Key** Bonus." **Whole path mangled to `I`-prefix** (ID/IH/IS/IU/IW/IE-001) and **Next Card = "ID-001 Key Bowl"** (wrong code + reused name/art).
