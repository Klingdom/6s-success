# On-device AI providers (Option A) — integration scaffolds

These files are the **native OS-model providers** for the tiered AI architecture, ready to drop into the Expo production build. They implement the same contract the app already routes through, so wiring them in is additive, not a rewrite.

> **Status: directional scaffolds, not compiled here.** I cannot build or device-test Swift/Kotlin in this environment. Treat every API call below as a shape to verify against current platform docs when you build. See the companion plan `../On-Device LLM - Native Integration Plan (Expo).html` for the reasoning behind these choices.

## What already exists (verified, in the PWA reference)

The app (`app/index.html`, built from `source/build_pwa2.py`, v0.3.0) already has the whole JS side of Option A:

- A **three-tier router** — `resolveTier(task)` returns `"device" | "cloud" | "static"` per task, driven by the AI mode the user picks in Settings (Off / On-device / Cloud).
- A **device provider seam** — `aiGenerate()` calls a device bridge when the tier is `device`, the cloud proxy when it is `cloud`, and falls back to the built-in static guidance otherwise.
- **Consent handling** — the one-time photo-send consent gate fires only for the cloud tier. On-device needs no consent because photos never leave the phone.
- A **capability probe** — `probeDeviceAI()` asks the bridge which tasks it can do (`sort`, `coach`, `text`) and caches the answer.

The bridge the reference looks for is `window.__6sLocalAI` (a WebView-host bridge). In a pure React Native build you expose the identical contract as an Expo native module instead; the method shapes are the same.

## The contract (both platforms implement this)

See `bridge-contract.ts`. Two methods:

```ts
availability(task: "sort" | "coach" | "text"): "available" | "downloadable" | "unavailable"
generate(req: { task; prompt: string; imageUris: string[] }): Promise<object>  // the task's strict JSON
```

`generate` returns the **same JSON shape the cloud tier returns**, so `clampSort` / `clampCoach` and the tolerant parser handle it unchanged:

- sort → `{ clutter_score, plan, belongs[], review[{item,verdict,why}], hazards[] }`
- coach → `{ score, meets_standard, coach, wins[], remaining[] }`

## Files

| File | Platform | Model path |
|---|---|---|
| `ios/OnDeviceAI.swift` | iOS | Foundation Models (text + guided generation) with the Vision framework as the image front-end |
| `android/OnDeviceAI.kt` | Android | Gemini Nano via ML Kit GenAI (image description) + Google AI Edge SDK |
| `bridge-contract.ts` | Both | The TypeScript contract + how the JS core calls it (native module and WebView bridge) |

## Wiring order (matches the plan's phased rollout)

1. Expo dev build (EAS) — none of this runs in Expo Go; each provider is a config plugin + a thin Expo native module.
2. Add the iOS provider first (text path via guided generation is the most reliable win), gate on `SystemLanguageModel` availability.
3. Add the iOS Vision front-end for the photo tasks; keep safety-critical calls on cloud.
4. Add the Android provider; gate on AICore availability.
5. Point the JS core's device bridge at the native module; the router already does the rest.
