# Code Analysis — inputs to the MVP Beta plan

Part III of the Product Specification was written from four parallel code-analysis passes over the v2.4 artifact (`6s-home-reset-app-v2.jsx`, 1,718 lines). This note records what those passes found, so the reasoning behind Part III is traceable.

## The four lenses

1. **Architecture & mobile port** — component tree, state, and what ports to Expo/React Native vs what must be rebuilt native.
2. **Feature & UX flow** — screen-by-screen actual capability, the core loop end to end, and MUST/NICE/CUT calls for a lean beta.
3. **Data, content & AI** — the embedded datasets, the instruction engines, the persistence schema, the photo pipeline, and the AI contracts.
4. **Security, privacy & store compliance** — data handling, photo privacy, AI safety, and the store-gating checklist.

## The findings that shaped Part III

**Every headline count is exact.** 20 rooms, 114 zones, 97 products, 1,812 mappings (Core 402 / Recommended 288 / Conditional 1,122), 291 retail picks, 684 activities, and 3,062 substeps were all counted in the code and match the spec.

**The app is a Claude artifact, not a shippable app.** Two dependencies must be replaced:
- Persistence runs through `window.storage` (an injected key-value store), with a chunked photo-write probe that exists only to survive the artifact's opaque quota. On a native file system that entire subsystem is deleted.
- The AI call is a `fetch` to the Anthropic API with **no key and no version header**, relying on the artifact host to inject credentials. A shipped binary must never embed the key; it needs a server proxy. This is a security blocker.

**Stale model + tight tokens.** The model id (`claude-sonnet-4-6`) and `max_tokens: 1000` should be revisited at build time; the tight cap is why the app carries an elaborate JSON truncation-repair layer.

**The one genuine catalog gap** is `Deep Drawer Bin Set` (product index 26), mapped to no zone though the Straighten engine has drawer logic. Five other unmapped items are system/method tools (red-tag kit, reset timer, before/after card, audit card, QR label kit) and are expected to have no zone surface.

**Defects to fix in the port:** the dashboard "items released" stat omits the relocate tally; the lightbox deletes a photo on one tap with no confirmation; checkable substeps look required but do not gate step completion; the rebrand is not applied anywhere in the UI.

**The core loop is genuinely complete** as static content plus local UI. The two decisions that make the beta are decoupling persistence and AI from the artifact host, and trimming content breadth (curated flagship rooms) and catalog depth (names and purpose only, no dated prices or deep links) to a maintainable set.

**Compliance P0 before any real home photo reaches a tester:** a zero-retention, no-training AI proxy with no embedded key; a privacy policy and terms; first-run consent and a pre-send notice; native camera/photo permission strings; and encryption at rest. Home interiors can contain faces, children, mail, and medication, so this is non-negotiable.

## Note

The analyses were run with the safety classifier temporarily unavailable, so their outputs were reviewed before being folded into the plan. The full per-agent transcripts live in the session task directory; this summary is the durable record.
