# Entryway Deck - Copy Spec (corrected, on-canon)

Edit the SOURCE template with this, then re-export front/back with bleed. Six S's: Sort, Straighten, Shine, Safety (4th), Standardize, Sustain. Never 'Set in Order'.

## Global fixes

- **"Set in Order" -> "Straighten"** (22 cards): Replace the 5S term in every 6S LESSON, and make each lesson name the S the card is about (see the tables). Also fix "Point of Use" on EM-008.
- **Friction meter -> Impact Level** (9 EP cards): Rename the Problem-card gauge "IMPACT LEVEL" (neutral 1-5) and tie it to the game (bigger impact = bigger reward + a per-turn penalty while unsolved). Keep "DIFFICULTY" on Micro-Zone cards and "PERMANENT / TEMPORARY BONUS" on Tool cards.
- **Correct the bonus badges** (ET-005, ET-012): A bench and a charger must not grant a "+1 Key Bonus." ET-005 -> +1 Seat Bonus; ET-012 -> +1 Device Bonus. Give every Tool a bonus that matches its object.
- **Lock one code scheme + validate links** (deck-wide): One canonical numbering (tables below). Every card's internal code must equal its filename. Kill all EN-/I-prefixes, self-references, "EVERTS," and "MICRO ZONES->ET-001" (Micro-Zone links must point to an EM card). Shrink the 9-slot path to the 2-3 real links shown.
- **Never generate body text into the image** (EM-005, EM-006, ET-007, EP-005): All titles, callouts, info rows, and the QR must be added by the template layer over a clean photo - this is the permanent fix for the garbled text and the fake QR. Remove all real brand logos (DYMO on ET-007, Amazon on EP-005).
- **Simplify the back + set print mechanics** (deck-wide): Collapse the back's bottom third to 3 checkboxes + <=5 code-less category icons. Add 3mm bleed + safe margin, one corner radius, defined green/red ink builds, hairlines >=0.75pt, and remove the FRONT/BACK proof labels.

## Micro-Zone cards (EM)

| Code | Name | S | Corrected 6S LESSON | Next | Problem / Tool | Fix |
|---|---|---|---|---|---|---|
| EM-001 | Front Door | Safety | A safe, clean start sets the tone for everything that follows. | EM-002 | EP-001 / ET-003 | START card |
| EM-002 | Landing Zone | Straighten | A defined landing zone gives everything you carry in one clear home. | EM-003 | EP-002 / ET-001 | retire stray EM-004 dup |
| EM-003 | Key Station | Straighten | Straighten means a home for every key, so mornings run on habit, not hunting. | EM-004 | EP-003 / ET-001 |  |
| EM-004 | Mail Station | Sort | Sort every piece as it lands: act, file, or recycle. Nothing waits in a pile. | EM-005 | EP-005 / ET-004 | was 'Set in Order' |
| EM-005 | Shoe Zone | Straighten | Straighten gives every pair a slot; Shine keeps the floor clean. | EM-006 | EP-009 / ET-003 | REGEN image |
| EM-006 | Coat Storage | Straighten | Straighten means a home for every coat, counted by weather, not number. | EM-007 | EP-006 / ET-002 | REGEN image |
| EM-007 | Backpack Station | Straighten | Straighten gives each pack a launch hook, so nothing lands on the floor. | EM-008 | EP-004 / ET-006 | AUTHOR |
| EM-008 | Pet Station | Straighten | Straighten keeps leash, bags, and food right where you use them. | EM-009 | EP-007 / ET-002 | was 'Point of Use' |
| EM-009 | Umbrella Station | Straighten | Straighten gives wet umbrellas a home that drips into a tray, not the floor. | EM-010 | EP-008 / ET-011 | was 'Set in Order' |
| EM-010 | Seasonal Storage | Sort | Sort today from tomorrow, so the entry holds this season and boxes the rest. | EM-011 | EP-010 / ET-008 | fix 'EVERTS' |
| EM-011 | Guest Welcome | Standardize | A standard-set, welcoming space lowers stress for guests and family alike. | EM-012 | EP-011 / ET-005 | drop 'Starting Room'; fix 'EVERTS' |
| EM-012 | Departure Checklist | Standardize | Visual controls create repeatable results. Standard work beats willpower. | ER-002 (Living Room) | EP-012 / ET-012 | fix all-'002' path |

## Problem cards (EP)

| Code | Name | S | Corrected 6S LESSON | Next | Zone / Tool | Fix |
|---|---|---|---|---|---|---|
| EP-001 | First Impressions | Safety | AUTHOR: a safe, clean, welcoming door is the fix. | EP-002 | EM-001 / ET-003 | AUTHOR |
| EP-002 | Landing Clutter | Straighten | AUTHOR: a defined landing zone is the fix. | EP-003 | EM-002 / ET-001 | AUTHOR |
| EP-003 | Lost Keys | Straighten | AUTHOR: one home for keys is the fix. | EP-004 | EM-003 / ET-001 | AUTHOR |
| EP-004 | Backpack Explosion | Straighten | Straighten means a launch hook for every pack, so nothing explodes onto the floor. | EP-005 | EM-007 / ET-006 | was 'Set in Order' |
| EP-005 | Package Pile | Sort | Sort each delivery on arrival, so packages flow through instead of stacking. | EP-006 | EM-004 / ET-004 | REGEN (Amazon) |
| EP-006 | Coat Pile | Straighten | Straighten gives every coat a home by the door where it's used. | EP-007 | EM-006 / ET-002 | was 'Set in Order' |
| EP-007 | Missing Dog Leash | Straighten | Straighten gives the leash one home at the point of use, so it's never lost. | EP-008 | EM-008 / ET-002 | was 'Set in Order' |
| EP-008 | Missing Umbrella | Straighten | Straighten gives umbrellas one home by the door, ready for rain. | EP-009 | EM-009 / ET-011 | was 'Set in Order' |
| EP-009 | Mud Trail | Shine | Shine means preventing problems, not just cleaning up after them. | EP-010 | EM-005 / ET-003 | keep -a; fix dup pin |
| EP-010 | Sports Gear Explosion | Straighten | Straighten gives each kit a bin at the point of use, so gear stops erupting. | EP-011 | EM-010 / ET-008 | fix self-link + zone name |
| EP-011 | Unexpected Guests | Standardize | A standard two-minute reset keeps the entry guest-ready any time. | EP-012 | EM-011 / ET-005 | fix self-link |
| EP-012 | Morning Rush | Sustain | Sustain means a nightly reset, so mornings run on the system, not on luck. | (campaign / done) | EM-012 / ET-012 | fix circular game-effect |

## Tool cards (ET)

| Code | Name | S | Corrected 6S LESSON | Next | Zone / Problem | Fix |
|---|---|---|---|---|---|---|
| ET-001 | Key Bowl | Straighten | Straighten means one home for keys, so you grab and go. | ET-002 | EM-003 / EP-003 | fix EN-001->EM-003; +1 Key |
| ET-002 | Wall Hooks | Straighten | Straighten hangs each coat at the point of use. | ET-003 | EM-006 / EP-006 | MICRO ZONES->EM; +1 Coat |
| ET-003 | Boot Tray | Shine | Shine stops grit at the door, protecting every floor in the house. | ET-004 | EM-005 / EP-009 | MICRO ZONES->EM; +1 Floor |
| ET-004 | Mail Sorter | Sort | Sort routes every piece of mail to a verdict, not a pile. | ET-005 | EM-004 / EP-005 | MICRO ZONES->EM; +1 Mail |
| ET-005 | Entry Bench | Straighten | Straighten gives a place to sit and a home for what's beneath. | ET-006 | EM-011 / EP-011 | BADGE Key->Seat; IW-001->EW-001 |
| ET-006 | Cube Organizer | Straighten | Straighten gives every category its own cube. | ET-007 | EM-007 / EP-004 | fix TOOLS self-link |
| ET-007 | Label Maker | Sustain | Labels make a home anyone can return to, so the system sustains itself. | ET-008 | EM-002 / - | REGEN (DYMO); tagline ok |
| ET-008 | Storage Basket | Straighten | A basket is a transition home, not a landing pile - Straighten with a purpose. | ET-009 | EM-010 / EP-010 | Temporary Bonus ok |
| ET-009 | Floating Shelf | Straighten | Straighten adds storage without using floor space. | ET-010 | EM-006 / - | fix 'without less'; self-link |
| ET-010 | Drawer Organizer | Straighten | AUTHOR: a section for every small thing. | ET-011 | EM-010 / - | AUTHOR |
| ET-011 | Umbrella Stand | Straighten | AUTHOR: a home that catches the drips. | ET-012 | EM-009 / EP-008 | AUTHOR |
| ET-012 | Charging Station | Straighten | Straighten gives devices one charging home, so cords and phones stop wandering. | (campaign / done) | EM-012 / EP-012 | REBUILD I-path->E; BADGE Key->Device; fix Next |

## Missing cards to author

- **EM-007 Backpack Station** - referenced by EM-006 Next and EP-004
- **EP-001 First Impressions** - referenced by many EM related-paths
- **EP-002 Landing Clutter** - referenced by EM related-paths
- **EP-003 Lost Keys** - referenced by EM related-paths
- **ET-010 Drawer Organizer** - referenced by ET-009 Next and EM-010
- **ET-011 Umbrella Stand** - deck jumps ET-009 -> ET-012