# On-device test script

Ten minutes, ten checks. Each one names exactly what to expect, so the answer is
a fact rather than an impression.

Everything in this app has been proven from source: it bundles, the corpus
matches the website, the merge rules are unit tested, no source file can reach
the network, and every control carries a role and a label. **None of that
required a phone, and none of it proves the app is usable on one.** These ten
checks are the part only a device can answer.

Write the result in the right-hand column. If something is wrong, the exact
words on screen are more useful than a description of them.

## Setup, about two minutes

1. Install **Expo Go** from the App Store or Play Store.
2. On the PC:
   ```
   cd C:\Users\philk\6s-success\mobile\quest-app
   npx expo start --lan
   ```
3. Phone on the same wifi as the PC. Scan the QR code in the terminal: use the
   **Camera** app on iPhone, or **Expo Go** itself on Android.
4. If the QR does not resolve, open `exp://192.168.1.7:8081` in Expo Go.
5. If nothing connects at all, Windows Firewall is the usual cause. Allow node
   for **private networks**, or run once in an admin PowerShell:
   ```
   New-NetFirewallRule -DisplayName "Expo dev" -Direction Inbound -LocalPort 8081 -Protocol TCP -Action Allow -Profile Private
   ```

## The ten checks

| # | Do this | Expect exactly this | Result |
|---|---|---|---|
| 1 | Open the app | A card, dark background. Top left a rounded badge reading **sort**. Top right **1 of 6** | |
| 2 | Read the card | Zone line: **Entryway > Landing Zone**. Heading: **The spot where pockets empty on the way in and refill on the way out.** Body begins **Empty the tray and the paper stack onto the floor** | |
| 3 | Scroll down | A panel headed **DONE LOOKS LIKE**, then **About 30-45 min for the whole zone.**, then an orange **Done** button and an outlined **Not now** | |
| 4 | Tap **Done** | Badge changes to **straighten**, count to **2 of 6**, and the text changes. It must not stay on sort | |
| 5 | Tap **Done** five more times, six in total | After the sixth pass in total you land on a finish screen headed **THAT IS A ZONE** with **Landing Zone** under it, six coloured dots, and the words **1 sort, 1 straighten, 1 shine, 1 safety, 1 standardize, 1 sustain** | |
| 6 | Read the line under the dots | **1 of 114 zones in the house is holding.** | |
| 7 | Tap **Draw the next card** | A card for **Entryway > Coat and Outerwear Zone**, badge **sort**, count **1 of 6** | |
| 8 | **Close the app completely** and reopen it | It returns to the Coat and Outerwear card, not back to the Landing Zone. Progress survived | |
| 9 | **Turn on airplane mode**, then close and reopen the app | It still opens and still works. This is the offline-first promise, and a garage or basement is the real terrain | |
| 10 | Turn on **VoiceOver** (iPhone) or **TalkBack** (Android) and swipe through the card | Each control announces as a **button** with a spoken name: "Mark this card done", "Not now", "Import progress from the web Quest". The six coloured dots on the finish screen are **skipped silently**, because their meaning is in the words beside them | |

## Two extra checks if you have another five minutes

| # | Do this | Expect | Result |
|---|---|---|---|
| 11 | On the PC open the web Quest, do two cards, press **Back up**, put the downloaded `6s-home-quest-progress.json` somewhere the phone can reach (email it to yourself, or Google Drive). In the app tap **Already used the web Quest? Import your progress** and pick it | A message saying how many cards were imported. Progress from the browser now shows in the app, and nothing you did on the phone is lost | |
| 12 | Increase the phone's text size to the largest setting and reopen the app | Text grows. Nothing is cut off, no button loses its label, no line runs off the screen | |
| 13 | Finish a second zone (six **Done** taps again), then on the finish screen tap **Stop here, this counts** instead of **Draw the next card** | A screen headed **Good stopping point.**, the zones-holding count, and one **Draw a card** button. Nothing pushes another card at you | |
| 14 | On that stopping screen, tap **Draw a card** | Returns to an open card, ready to continue | |

## What each check is actually for

- **1 to 3** prove the corpus reaches the screen intact and the card is readable.
- **4 to 7** prove the loop: draw, do, done, advance, finish a zone, start the
  next. This is the entire product.
- **8** proves progress persists, which is what makes a quest you pick up over
  several days possible at all.
- **9** proves offline-first, which is a stated non-negotiable and the reason
  the app has no network calls in it.
- **10** proves the accessibility semantics added on 2026-08-31 actually reach
  the screen reader. Contrast, touch targets and Dynamic Type were measured
  from source and pass; announcement is the part only a device can settle.
- **11** proves web to mobile import end to end. The merge rules are unit tested
  and a real browser backup has been fed to the real parser, but nobody has
  picked a real file on a real phone.
- **12** proves Dynamic Type does not break the layout.
- **13 and 14** prove the two finish-screen buttons actually do different
  things: "Stop here, this counts" has to genuinely stop rather than draw
  another card in disguise, the exact bug fixed on 2026-09-02.

## If something fails

Send the check number and the exact words on screen. A screenshot is better
still. Do not work around it: a failure here is worth more than a pass, because
every one of these is currently an assumption.
