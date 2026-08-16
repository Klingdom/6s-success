# 6S Success Home Micro Zones: Organization & Housekeeping — MVP Beta (first attempt)

A **runnable, on-device mobile web app / PWA** — the first working attempt at the MVP, built and verified in a browser. It implements the full core zone-reset loop off the Claude artifact host, which is exactly the thing the spec said the beta must prove.

Store listing title: **6S Success Home Micro Zones: Organization & Housekeeping**. Short app name: **6S Micro Zones**.

## v0.2 (rebuilt from the review panel)

This is v0.2, rebuilt to apply the seven-discipline review panel's Tier-1 fixes and then re-reviewed by a four-discipline panel. What changed since v0.1:

- **On-device instrumentation.** Privacy-safe loop events (setup, zone_started, step_completed, zone_completed, photos added, AI requested/failed, coach_review, audit_action) plus a health family (storage_mode, storage_write_failed, photo_decode_failed, app_error), all counts and enums only, nothing transmitted. A **Diagnostics** screen shows them.
- **Before/after completion reveal**, gated on both a before and an after photo, with items-released and a next-zone button. Completion now fires (and reveals) whether you finish via the last step or the last photo.
- **AI off-state** (explicit, not a dead button) with a loading state, Cancel, and a Retry on recoverable errors; AI JSON is clamped before render.
- **In-app help + a photo-free diagnostic export** (no photos, names, or endpoint URL) and an **error boundary** with a recovery screen.
- **Fixes:** items-released is donate + discard (relocate tracked separately); measured session time; honest in-memory-storage notice; accessibility affordances (aria labels, keyboard-operable thumbnails, larger tap targets).

`review/MVP v0.2 Rebuild Review.html` holds the four-discipline verification of these fixes, the issues found, and improvement ideas. The high and medium issues that review surfaced (the reveal not showing on the photo path, completion double/under-counting, session_minutes reading zero, the diagnostic hostname leak) were then fixed and re-verified in-browser; the report lists them at the top.

## What it is (and is not)

This is the runnable-web / PWA first attempt you approved, not the production native build. Its logic is the same logic that ports to Expo / React Native next. It runs on a phone browser today and can be installed to the home screen.

## Run it

**On a computer (quickest look):**
```
cd app
python -m http.server 8741
```
Open `http://localhost:8741/` and resize the window narrow, or open your browser dev tools device mode.

**On your phone (recommended):**
1. Serve the `app/` folder from your computer as above.
2. On the phone browser, go to `http://<your-computer-ip>:8741/` (same Wi-Fi).
3. Use "Add to Home Screen" to install it as an app. (Photos persist and the service worker/offline cache work when served over http or https, not from a bare `file://` open.)

## What works (verified in-browser)

- **Setup** → household name + the 6 curated beta rooms (Entryway, Kitchen, Primary Bathroom, Primary Bedroom, Home Office, Laundry = 37 zones).
- **Dashboard** → zones-reset / time / items-released stats, a "Next up" card, room cards with progress rings and zone-dot strips.
- **Zone runner** → mission (function, done-state, watch-for, expert cue), before/after photo galleries (camera + upload, compressed on-device), the AI Sort-plan block, six color-coded step panels with the **real ported content engine** (zone-adaptive substeps, product chips, the Sort out-the-door tally), done/undo, the coach-review block, and the sustain audit.
- **Product sheet** → level, purpose, "I own this" toggle, and the three sourced-pick names (no dated prices or links in the beta).
- **Settings** → AI endpoint, household name, and full data wipe.
- **Persistence** → progress and tallies in localStorage, photos in IndexedDB (with an in-memory fallback), verified to survive a full reload. No console errors.

## AI (optional, off by default)

The app never holds an API key. AI Sort plans and coach reviews are **off** until you set an endpoint in **Settings → AI endpoint**. That endpoint is a small server proxy that holds the key. A working example is in `proxy/ai-proxy-example.js`:

```
cd proxy
npm init -y && npm install express
ANTHROPIC_API_KEY=sk-... node ai-proxy-example.js
```
Then set the app's AI endpoint to `http://<your-host>:8787/ai`. Without an endpoint the app runs fully on the built-in static guidance (it degrades gracefully, exactly as the spec requires).

## How this maps to the spec's MVP plan

- **Decoupling workstream 1 (persistence off the artifact):** done here with localStorage + IndexedDB behind a small storage layer.
- **Decoupling workstream 2 (AI via proxy, no key in the app):** done here as a configurable endpoint plus the example proxy.
- **Curated rooms, product names only, minimal sustain audit, single-user, on-device:** all as scoped.
- The **content engine, AI prompts, JSON-repair, and component logic are ported from the v2.4 artifact**, so the same code carries into the Expo build.

## Honest limits of this first attempt

- **It is a web app, not the native build.** The production target remains Expo/React Native; this proves the loop and the two decouplings, and serves as the reference implementation to port.
- **Photo capture and AI were verified by code and by the app's own flow, not by a live camera upload or a live API call in this environment.** Test both on a real phone with a real proxy before relying on them.
- **The P0 compliance items in the spec are not built here** (privacy policy, consent screen, permission strings live in the native shell, encryption at rest, a zero-retention proxy configuration). Do not put real testers' home photos through a live AI proxy until those are in place.
- Curated to 6 rooms; the other 14 rooms and the full catalog depth are deferred exactly as the spec says.
- Model id and token cap mirror the artifact (`claude-sonnet-4-6`, ~1200 tokens); confirm the current model when you wire the real proxy.

## Files

```
app/
  index.html            the whole app (self-contained: data + engine + UI + storage)
  manifest.webmanifest  PWA manifest
  sw.js                 service worker (offline cache)
  icon.svg              app icon
proxy/
  ai-proxy-example.js   minimal key-holding AI proxy (Express)
README.md
```
