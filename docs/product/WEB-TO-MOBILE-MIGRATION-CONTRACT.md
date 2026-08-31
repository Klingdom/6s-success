# Web to mobile migration contract

Backlog item 5B.2's own acceptance line: "the contract states what moves,
what changes and what a web user keeps when they install." This document is
that contract, on its own rather than folded into `PRD.md`, since it is the
one artifact 5B.4 and 5B.5's own device verification will need to check
against directly. Written 2026-08-31 against `main` at `cad4747f`, grounded
in `docs/audit/CURRENT-STATE-AUDIT.md` (5B.1) and the merge logic already
built and unit tested in `mobile/quest-app/lib/importProgress.js` (5B.5).

**No installs have happened yet.** Nothing in this document is a measured
result; the picker flow it depends on has not run on a real device (5B.4's
own open item). It is a contract in the sense of a stated promise to keep,
checked here for internal consistency against real code, not a report of
something already verified end to end on a phone.

## 1. What moves automatically: nothing

There is no automatic migration. A web user installing the app gets a
brand-new, empty local state (`AsyncStorage` under `6s.quest.v1`), separate
from whatever `localStorage` holds in their browser. This is a deliberate
consequence of the "no account, no network calls at all" decision recorded
in `PRD.md` Section 5, not an oversight: the only way to carry progress from
a browser to a phone without an account or a server is for the user to
carry it themselves.

## 2. What a web user has to do to bring their progress over

1. On the web Quest, use the existing export control (`backup()` in
   `site/assets/js/quest.js`), which writes a JSON file shaped
   `{ done: { cardId: timestamp } }`.
2. Get that file onto the phone (AirDrop, email to self, cloud drive,
   whatever the user already uses; the app does not prescribe a transfer
   method).
3. In the app, use "Already used the web Quest? Import your progress"
   (built in 5B.5, wired into `App.js`), which opens the OS document picker
   via `expo-document-picker`.
4. The picker hands the file to `parseBackup()`, then `mergeDone()` merges
   it into the app's own `done` map.

**Not yet verified on a real device:** step 3's picker itself. 5B.1 and
5B.5 both name this as the same open wall as 5B.4. This contract's
Section 5 acceptance criteria are written so they can be checked the
moment a phone is available, without redesigning anything first.

## 3. The merge rule, and why it is safe

`mergeDone(existing, incoming)` keeps, for every `cardId` present on either
side, whichever timestamp is earlier. Read directly from
`lib/importProgress.js` rather than assumed:

- A card done on the phone but never on the web: kept as-is.
- A card done on the web but never on the phone: added.
- A card done on both, at different times: the earlier timestamp wins,
  meaning the import can never make a card look freshly done when it was
  actually completed earlier on the other device, and it can never erase
  work already recorded on the phone.
- A card not done on either side: absent from the result, same as before.

**Why the earlier-wins rule specifically, not later-wins or a full
overwrite:** the timestamp records when the physical work happened, not
when the data arrived on this device. A later import should never make a
card read as "just finished" if it was actually finished a week earlier on
the other device; that would corrupt the recommendation/audit-due engine's
own cadence math (`daysSince`, Section 6 of `PRD.md`) the moment it ships
on mobile, since it depends on the true completion date. Verified against
this exact concern by `lib/importProgress.test.js`'s synthetic full-house
test (5B.5): merging 684 real cards from the corpus drops or invents
nothing.

## 4. What changes, feature by feature

Everything in `docs/audit/CURRENT-STATE-AUDIT.md`'s parity table, stated
here as a direct promise to the installing user rather than a gap list:

| On the web today | On first install | After import |
|---|---|---|
| 684 cards, 20 rooms, 114 zones | same corpus, same S order | same |
| Random draw, room mode, one-S mode | sequential walk only (mode selection is `PRD.md` Section 6, gap 2, not yet built) | same as first install; import does not add modes |
| Timer | absent (`PRD.md` Section 6, gap 5) | same |
| Photo capture | absent (`PRD.md` Section 6, gap 3) | photos taken on web are **not** carried over; only the `done` map is a photo cannot travel through a JSON backup file the way a timestamp can, and no photo-transfer path exists |
| Recommendation / audit-due engine | absent (`PRD.md` Section 6, gap 1) | absent; imported timestamps are ready to feed it the moment it ships, but nothing reads them for recommendations yet |
| Streak | absent | absent, and its exact semantics are an open question (`PRD.md` Section 7) |
| Progress map (visual) | zone/house counts only | same; counts reflect the merged `done` map correctly, a map view does not exist yet |
| First-run gate | none (every launch behaves the same) | none |
| Analytics | none | none (`PRD.md` Section 11) |
| Backup export from the phone itself | not built; import only | not built; a phone user cannot yet hand their progress to a second device or back to a browser |
| Offline | yes (service worker) | yes, natively, no service worker needed |
| Accounts | none | none |

**The one-directional gap worth stating plainly:** a user can bring web
progress into the app, but cannot yet take app progress back out to the web
or to a second phone. Building export-from-mobile is not scheduled in this
document; it is a natural pairing with import and should be picked up
alongside it rather than treated as separately optional, but it is not
built today and this contract does not claim otherwise.

## 5. What a web user keeps, stated as commitments

These are the promises this contract makes, each checked against real code
rather than asserted:

1. **No data loss on import.** Guaranteed by the merge rule in Section 3,
   proven for the full 684-card corpus by `lib/importProgress.test.js`.
2. **No account required, on either platform, ever, for the free core.**
   Matches `PRD.md` Section 8's entitlement hypothesis and CLAUDE.md's rule
   against gating something already free.
3. **The free tier is the entire product as it exists today.** There is no
   reduced "mobile free" version; every card, room and zone in the corpus
   is present (`assets/quest-corpus.json`, confirmed 20/114/684 in 5B.1),
   with the parity gaps in Section 4 being genuinely unbuilt features, not
   a deliberately smaller free offering.
4. **Photos already taken stay wherever they were taken.** A web photo does
   not silently vanish; it stays in the browser's IndexedDB exactly where
   it was, since nothing in the import path touches it. The gap is that it
   also does not travel to the phone, which Section 4's table states rather
   than hides.
5. **S order and Safety-fourth never change between platforms.** Both read
   the same generated corpus (`ops/build_mobile_corpus.py --check`
   detects drift), so a zone cannot show a different step order on the
   phone than it does in the browser.
6. **Nothing about installing the app sends anything over the network.**
   The app has zero network calls today (5B.1, confirmed against the
   dependency list); installing and importing are both fully offline
   operations.

## 6. Acceptance criteria for closing this contract's open items

Written now so 5B.4 (or whoever holds a real phone next) can check against
something concrete rather than re-deriving what "verified" should mean:

- The document picker (Section 2, step 3) successfully opens and returns a
  file path on at least one real iOS or Android device via Expo Go.
- A JSON file actually produced by clicking "export" on the live web Quest
  (not a hand-written fixture) imports without error and the app's
  zone-held counts match what the browser showed before export.
- Importing the same file twice does not double-count or corrupt anything.
  Already true in the merge logic and already tested: read
  `lib/importProgress.test.js` directly rather than assuming, and it has
  its own case, "importing the same backup twice is idempotent," which
  merges the same incoming file against its own already-merged output and
  asserts nothing changes on the second pass. What is still unverified is
  only that a real device produces the same file both times through the
  actual OS picker, not the merge logic itself.
- The one-directional gap in Section 4 is either resolved (export-from-
  mobile built) or still accurately described here; this document should
  be re-read and corrected the moment either changes, not left to drift the
  way `deck.html` was found describing a retired product for days
  (5.8's own retrospective note).
