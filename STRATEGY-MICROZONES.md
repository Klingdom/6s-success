# Micro zones: what the moat actually is, and how to productise it

Written 2026-09-24 on Phil's direction to double down on micro zones. Evidence
first: every number here was measured from `content/manual/source/content.json`
and the built site, not estimated.

---

## 1. The asset, measured

20 rooms, 114 micro zones. Per zone the corpus holds:

<!-- COVERAGE:BEGIN -->

| Field | Zones with it | Sub-items | What it is |
|---|---|---|---|
| purpose, done_looks_like, session, time_note | 114 | - | what this place is for and when it is finished |
| passes | 114 | **684** | the six S steps, per zone |
| shine_detail | 114 | **762** | a cleaning method per surface, with product and order |
| watch_for | 114 | **252** | what goes wrong here |
| leave_behind | 114 | **228** | the standard that stays, and its trigger |
| the_call | 114 | **235** | the judgement call this zone forces |
| **diagnosis** | **38** | 118 | symptom to branching question to root cause |
| **capacity** | **38** | 76 | how much actually fits, and the test for "it does not" |
| **variants** | **38** | 76 | what to do when your home is not the assumed one |

**That split is the whole strategy.** The top block is complete and is already sold: the Print Pack ($19) carries the 684 passes, the Micro Zone Manual ($29) carries the clean-and-shine steps. The bottom block is the differentiator and it exists for **38 of 114 zones, 33.3%**, across 6 fully personalised rooms: Entryway (5), Kitchen (7), Primary Bathroom (7), Laundry Room (6), Home Office (6), Garage (7).

<sub>Measured from `content/manual/source/content.json` by `ops/build_microzone_coverage.py`. Do not hand-edit.</sub>

<!-- COVERAGE:END -->

## 2. Why the bottom three fields are the moat

An organising book tells you how to tidy a drawer. So does every blog. What
none of them does is this, from the Entryway Landing Zone:

> **Capacity.** One tray, sized for keys and sunglasses plus one wallet and one
> phone per adult who uses this door, and a single upright folder that stays
> under ten sheets.
>
> **The test for "it does not fit".** If a real folder, worked down honestly
> every week, still will not stay under ten sheets, the tray and folder are
> undersized for this house.

That is a falsifiable standard. It tells a household that their furniture is
wrong, which is a thing no generic advice can say because generic advice does
not know how many adults use the door.

`variants` does the same for homes that do not match the assumption ("no
console, only a wall by the door"). `diagnosis` turns a symptom into a root
cause through branching questions, which is `CLAUDE.md` sections 5 and 6 in
working form: understand the function, find the root cause, then prescribe.

**So today the product does what it says it does for 12 zones out of 114.**
Closing that is not new content. It is making the shipped product match its own
stated philosophy.

## 3. What completing it unlocks, in order of value

1. **The app can actually diagnose.** The Home Quest's symptom entry currently
   has real branching for the pilot zones only. Every completed room widens
   what a household can be asked about.
2. **A new product tier that nothing on the market matches: the Room Plan.**
   For one room: the zones in working order, sized to your home (capacity),
   adapted to your situation (variants), aimed at the friction you actually
   named (diagnosis). The $9 room pack is the natural vehicle; it currently
   carries steps, not a plan.
3. **Free-layer depth that earns discovery.** Each completed zone page gains a
   capacity rule and a variants block, which are the passages most likely to
   be quoted by an answer engine, because they answer a question no one else
   answers.

## 4. The unit of work is a room, not a zone

Every room completed so far was done whole, and that is the right unit: a
half-personalised room cannot ship as a Room Plan, and the app cannot offer
diagnosis for a room where only some zones branch. The table above names which
rooms are finished, and it is measured, so it cannot drift from the corpus.

The order is the owner's own stated launch order (the affiliate brief's launch
rooms were Entryway, Kitchen, Primary Bathroom, Home Office, Laundry Room,
Garage). Entryway, Kitchen, Primary Bathroom and Home Office are done, so the
next two are **Laundry Room** and then **Garage**. After those, the remaining
fourteen rooms are unordered and should be picked by which rooms the site's
own zone pages are actually being read in.

## 5. The rule that keeps this honest

Nothing in these three fields may be invented. The 12 existing ones were
authored from each zone's own `purpose`, `done_looks_like` and `passes`, and
the capacity numbers are derived from the objects the zone already names. A
capacity rule that guesses a number is worse than no capacity rule, because a
household can measure it and find it wrong.

## 6. What this supersedes

`DECISIONS.md` D-021 gated M6, the remaining 102 zones' diagnosis layer, on
genuine human readers or a Search Console read. That gate was mine and it was
correct on the evidence available: the work was ahead of the constraint.

Phil has now directed the opposite, on product grounds rather than traffic
grounds. Owner direction outranks an autonomous gate, and the case is
different from the one D-021 answered: this is not "will more pages bring
traffic", it is "does the product do what it claims". It does not, for 89.5%
of the house.
