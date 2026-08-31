# 6S Success Home Quest, mobile MVP

The core loop and nothing else: draw one card, do one bounded job, mark it done,
stop without guilt or continue by choice.

Verified 2026-08-31: dependencies resolve (1,131 packages), the app bundles
(539 modules, 1.73 MB), and Metro serves it over the LAN.

## Test it on a phone in about two minutes

1. Install **Expo Go** from the App Store or Play Store.
2. On this PC:
   ```
   cd mobile\quest-app
   npx expo start --lan
   ```
3. Phone on the same wifi. Scan the QR code in the terminal with Expo Go on
   Android, or with the Camera app on iPhone.

If the QR does not resolve, open `exp://192.168.1.7:8081` in Expo Go directly.

Windows may ask about the firewall the first time. Allow it for **private
networks**.

## What it does today

- Draws the first unfinished card, walking the corpus in its own order. A person
  coming back continues where the house was left rather than being handed an
  unrelated room.
- Shows the room, the zone, which of the six passes it is, the purpose, one
  bounded job, and what done looks like.
- Marking it done advances. Six passes complete a zone, and the finish screen
  recaps the session as coloured dots plus the same counts in words.
- Progress survives closing the app, held in AsyncStorage under `6s.quest.v1`,
  the same key the web app uses.

Safety is the fourth S. The corpus fixes the order and this app never reorders
it.

## What it deliberately does not do

Each of these is a decision, not an unfinished feature:

- **No account.** A user has to get real value before being asked to make one.
- **No network calls at all.** A garage has no signal, and a photograph of
  somebody's home must not leave the device.
- **No streaks, urgency or manufactured engagement.** Progress represents real
  work or it represents nothing.

## Where the content comes from

Not from a copy. `assets/quest-corpus.json` is a build product:

```
python ..\..\ops\build_mobile_corpus.py            # regenerate
python ..\..\ops\build_mobile_corpus.py --check    # fail if stale
```

It is derived from `site/assets/js/quest-data.js`, the same corpus the website
uses, and records that file's sha256 so drift is detectable. 20 rooms, 114
zones, 684 cards, matching the site exactly.

This matters because copying was the obvious shortcut and this repository has
been paying for that shortcut all fortnight: `mcp/content.json` drifted from its
source for twelve days and blocked an image publish, and 123 of 161 duplicated
filenames across the estate have diverged.

## What is next, and what blocks it

Unblocked: core loop parity checks on a real device, web to mobile import of a
Quest backup file, accessibility on device.

Blocked, and on what:

| Needs | For |
|---|---|
| Apple Developer account | any iOS build or store submission |
| Google Play account | Android submission |
| Java locally, or an Expo cloud account | a native Android build |
| The accounts layer | household play, and 6S Plus |

The last one is the largest gap in the business, not just this app: it is
$11,250 of the $21,500 month twelve model.
