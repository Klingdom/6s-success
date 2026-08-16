# Build & test the Apple on-device AI module

Complete, drop-in Expo local module: private, offline AI Sort plans and coaching reviews on-device via **Foundation Models + Vision**. Everything here is build-verified **by you on a Mac** (this was authored on Windows and cannot be compiled here). It is written to be correct and complete; verify the two fast-moving frameworks (Foundation Models, Expo Modules API) against current docs as you go.

## What this module does

- `availability(task)` → `"available" | "downloadable" | "unavailable"` (sync)
- `generate({ task, prompt, imageUris })` → the task's strict JSON

Output matches the cloud tier exactly, so the app's `clampSort` / `clampCoach` consume it unchanged. On-device means **photos never leave the phone**, so no consent gate fires (the app already handles this: consent is cloud-only).

## Prerequisites

- **macOS + Xcode 26** (or later) — the iOS 26 SDK is required to *compile* the Foundation Models APIs.
- A **physical Apple Intelligence device** for real testing (iPhone 15 Pro or later, or an M-series iPad). On anything older the module compiles and links but reports `unavailable`, and the app falls back. Simulator support for the model varies; test on device.
- Node 18+, an Expo project on a recent SDK (Expo Modules API), and an **EAS dev build** or local `expo run:ios`. **None of this runs in Expo Go.**

## 1. Place the files (Expo local module layout)

Create `modules/on-device-ai/` in your Expo app and map these files:

```
modules/on-device-ai/
  package.json                 <- package.json
  expo-module.config.json      <- expo-module.config.json
  index.ts                     <- index.ts
  expo-plugin.js               <- expo-plugin.js
  ios/
    OnDeviceAI.podspec         <- OnDeviceAI.podspec
    OnDeviceAI.swift           <- OnDeviceAI.swift
    OnDeviceAIModule.swift     <- OnDeviceAIModule.swift
```

(That is: everything except the two `.swift` files and the `.podspec` sits at the module root; those three go in `ios/`.)

## 2. Register the config plugin

In `app.json` / `app.config.js`:

```json
{ "expo": { "plugins": ["./modules/on-device-ai/expo-plugin.js"] } }
```

## 3. Wire it into the app's AI router

The app already has the tiered router (`resolveTier` / `aiGenerate`) and a device seam. Pick the path that matches how the core runs in your app:

### Path A — React Native core (if/when you port the UI to RN)

In the core's device-generate seam, call the module:

```ts
import LocalAI from "../modules/on-device-ai";

// availability probe (populate the app's deviceAICaps):
const status = LocalAI.availability("sort");        // "available" -> device tier is eligible

// generate:
const result = await LocalAI.generate({ task: "sort", prompt: beforePrompt(zone), imageUris });
```

### Path B — WebView-hosted core (fastest: reuse the verified HTML app)

The reference core probes for `window.__6sLocalAI`. Install it inside the WebView by injecting a shim that relays to RN, which calls the native module:

```tsx
// RN side (react-native-webview)
const INJECT = `
  window.__6sLocalAI = {
    availability: (task) => window.__6sCaps ? (window.__6sCaps[task] || "unavailable") : "unavailable",
    generate: (req) => new Promise((resolve, reject) => {
      const id = Math.random().toString(36).slice(2);
      window.__6sPending = window.__6sPending || {};
      window.__6sPending[id] = { resolve, reject };
      window.ReactNativeWebView.postMessage(JSON.stringify({ __6s: true, id, req }));
    })
  };
  true;
`;

<WebView
  source={{ uri: "app/index.html" }}
  injectedJavaScriptBeforeContentLoaded={INJECT}
  onMessage={async (e) => {
    const msg = JSON.parse(e.nativeEvent.data);
    if (!msg.__6s) return;
    try {
      const out = await LocalAI.generate(msg.req);
      webRef.current.injectJavaScript(
        `window.__6sPending['${msg.id}'].resolve(${JSON.stringify(out)});true;`);
    } catch (err) {
      webRef.current.injectJavaScript(
        `window.__6sPending['${msg.id}'].reject(new Error(${JSON.stringify(String(err))}));true;`);
    }
  }}
/>
```

Push capabilities into the WebView once at load: probe `LocalAI.availability("sort"|"coach"|"text")` in RN and `injectJavaScript("window.__6sCaps = {...}; true;")`.

## 4. Build & run

```bash
npx expo prebuild -p ios      # generates ios/ and links the local module
npx expo run:ios              # dev build on a connected device
# or: eas build -p ios --profile development
```

## 5. Test harness

### Swift unit test (fastest confidence the provider works)

Add `OnDeviceAITests.swift` to your test target with a sample photo `messy_entry.jpg` in the test bundle:

```swift
import XCTest
@testable import OnDeviceAI      // adjust to your module/product name

final class OnDeviceAITests: XCTestCase {
  func testAvailability() {
    let s = OnDeviceAI.shared.availability(task: "sort")
    XCTAssert(["available","downloadable","unavailable"].contains(s))
    print("availability:", s)
  }

  func testSortGeneratesSchema() async throws {
    guard OnDeviceAI.shared.availability(task: "sort") == "available" else {
      throw XCTSkip("no Apple Intelligence on this test device")
    }
    let url = Bundle(for: Self.self).url(forResource: "messy_entry", withExtension: "jpg")!
    let out = try await OnDeviceAI.shared.generate(
      task: "sort",
      prompt: "ZONE: Entryway landing surface. Plan a Sort pass.",
      imageUris: [url.absoluteString])
    XCTAssertNotNil(out["clutter_score"])
    XCTAssertNotNil(out["plan"])
    XCTAssertNotNil(out["hazards"])
    print("sort result:", out)
  }
}
```

### JS smoke test (end to end, in the running app)

This mirrors exactly what was already verified in the PWA with a mock bridge — now with the real model:

1. Settings → AI coaching → **On-device**. On an eligible device the detail line shows **"Ready on this device."**
2. Open a zone, add a before photo, tap **Build my Sort plan**.
3. Expect: **no consent sheet**, a real plan renders, and the fineprint reads **"Generated on your device. Photos did not leave your phone."**
4. Finish the zone, tap **Get my review** → a scored review with the same on-device fineprint.
5. Turn on Airplane Mode and repeat — it still works (that is the whole point).

Confirm no photo egress with a network proxy (Charles/Proxyman): during on-device calls there should be **zero** outbound image traffic.

## Gotchas & policy

- **Availability gating is mandatory.** Never assume the model is present; the module already returns `unavailable` and the app routes around it.
- **iOS 26 to compile, older to run.** The FM code is `@available(iOS 26.0, *)` guarded and the frameworks are weak-linked, so the app launches on older iOS and simply falls back.
- **Vision is coarse.** It reads labels, text, and a saliency-based clutter estimate, not a full scene understanding. Keep the sharp **safety-hazard** calls on the cloud tier; the on-device instructions already tell the model not to claim it caught every hazard.
- **Guided generation is your JSON guarantee.** The `@Generable` structs enforce the schema, so there is no fragile parsing on iOS (unlike the Android path).
- **Calibrate the score.** Once real output is flowing, sanity-check that on-device clutter scores track the cloud tier's for the same photos, so the number feels stable if a user switches modes.
