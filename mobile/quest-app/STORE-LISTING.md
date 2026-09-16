# App store listing: what is ready, what is not

The plan promised that day one after the developer accounts exist would be a
submission, not a scramble. This is that preparation. Every field below is
written to be pasted. Where something is genuinely missing, it says so rather
than offering a placeholder that would be submitted by accident.

## 1. The two blockers, stated plainly

| Blocker | Who | Cost | Without it |
|---|---|---|---|
| Apple Developer account | Phil | $99/yr | No iOS build, no TestFlight, no listing |
| Google Play account | Phil | $25 once | No Android build, no listing |
| Screenshots on a real phone | Phil, 10 minutes | free | Both stores reject a listing without them |

Everything else on this page is done.

## 2. Screenshots: why they are not generated

Both stores require screenshots of the running app. There is no iOS simulator
on a Windows machine and no Android emulator installed here, so the only honest
source is Phil's own phone during the on-device pass in `ON-DEVICE-TEST.md`.

A web capture of `quest.html` dressed up as a phone screenshot would be a false
claim to a review team about software they are approving, so it will not be
done. Six captures are wanted, in this order: the card, a finished zone, the
finish screen with its picture, the progress line, the diagnostics screen, and
the import screen.

## 3. The fields, ready to paste

**App name (Apple, 30 char max):** 6S Success Home Quest
Counts 21 characters, so it fits both stores without truncation.

**Subtitle (Apple, 30 max):** One zone, one job, put it down
Counts 30, the exact limit. The full-stop version measured 31, one over,
which is a bounced submission rather than a warning. Both counts here are
checked by gate_store_listing_lengths in preflight, because this file was
twice written with a hand-guessed number that was wrong.

**Short description (Play, 80 max):**
Draw a zone, do one small job, put it down. 114 micro zones, works offline.
Counts 75.

**Full description (Play 4000 max, Apple description):**

Most home organizing advice asks you to clear a whole room. This does not. It
gives you one micro zone at a time, one job, and a plain description of what
done looks like, then gets out of your way.

114 micro zones across 20 rooms, from the landing zone by your front door to
the shelf where the cleaning supplies live. Each zone is finished with the same
six moves: sort, straighten, shine, safety, standardize, sustain. You draw a
card, you do the job on it, and the zone holds until it stops holding.

- Works completely offline. Nothing to sign up for.
- Your progress stays on your phone. No account, no email, no cloud.
- 106 of the 114 zones show what the finished zone looks like.
- 12 zones link a short video of the work, if you would rather watch first.
- Every job names its own finish line, so you know when to stop.

This is the phone version of the Home Quest on 6s-success.com. It is the free
entry point to the 6S method, not a trial with a paywall in the middle.

**Category:** Lifestyle. Secondary: Productivity.
**Content rating:** Everyone. No user content, no ads, no purchases, no links
except the optional zone videos on YouTube.
**Support URL:** https://6s-success.com/contact
**Marketing URL:** https://6s-success.com/quest
**Privacy policy URL:** https://6s-success.com/privacy

**Apple keywords (100 char field, comma separated, no spaces):**
organize,declutter,cleaning,checklist,habit,routine,home,tidy,chores,5s,zones,housekeeping
Counts 90 of the 100 allowed.

## 4. Data safety and privacy, answered from evidence

Both stores take these as formal attestations, so each answer below was checked
against the source rather than recalled.

**Does the app collect or share any data? No.**

Evidence: a grep of the whole app source for `fetch(`, `XMLHttpRequest`,
`axios`, `WebSocket`, analytics and crash-reporting clients returns exactly one
outbound call in the entire codebase, `Linking.openURL` on the optional zone
video. There is no analytics SDK, no crash reporter, no update client, and no
account system to attach data to.

| Store question | Answer | Why |
|---|---|---|
| Data collected | None | No network calls except the video link the person taps |
| Data shared | None | Nothing leaves the device |
| Account required | No | There is no account system |
| Ads | None | No ad SDK is present |
| Third-party analytics | None | No analytics dependency exists |
| Encryption in transit | N/A | Nothing is transmitted |
| Data deletion request path | Uninstall, or Reset in the app | Progress lives in on-device storage |
| Children's privacy | No data collected from anyone | Same answer for every age |

**One disclosure to make, not hide:** tapping *Watch this zone* opens YouTube in
the browser or the YouTube app. From that moment YouTube applies its own
policies. The app itself sends nothing, and nothing is requested from YouTube
until the person presses the link. Twelve of the 114 zones offer one; the other
102 show no link at all.

Progress is stored with AsyncStorage under a single key on the device.

## 5. Price: free, and the reasoning

**Decision: the app ships free, with no in-app purchase in the first release.**

Three reasons, in order of weight.

**1. The shop already promises it.** The live catalogue carries `APP-FREE`,
"The Home Quest, web app, free", with the line "No email, no account, nothing
to install." A paid phone app would contradict a promise customers can read
today. Changing the store listing is cheap; contradicting the shop is not.

**2. The app is the top of the funnel, not the product.** The things worth
money are the packs: 109 micro zone packs at $4, 19 room packs at $9, 15
situation kits at $14, 6 area bundles at $16, the eBook at $9.99, the Whole
House Print Pack at $19, the Micro Zone Manual at $29 and the Complete Digital
Bundle at $49. Every one of those is bought by somebody who already believes
the method works. Charging $3 at the door to protect a $49 bundle is the wrong
trade.

**3. The store cut is real and must not be absorbed quietly.** Apple and Google
take 15 to 30 percent. The web checkout takes none. Selling a $9 room pack
through in-app purchase nets $6.30 to $7.65 for the same work, so any future
in-app catalogue needs either a higher in-app price, which punishes the
customer for the platform they chose, or a deliberate decision to accept a
thinner margin for the reach. That is a business decision for Phil with real
numbers attached, not a default to drift into.

**What free does not mean.** No ads, no trial, no paywall mid-quest, no
"unlock the rest of your house" gate. The 114 zones are all present in the free
app. If a paid tier ever appears it should be for things the free app does not
do at all, such as household play across phones, rather than for withholding
zones that already work.

**Revisit when:** the accounts decision (gate 4) is made, because household
play and 6S Plus are the first things genuinely worth charging for, and both
need the accounts layer first.
