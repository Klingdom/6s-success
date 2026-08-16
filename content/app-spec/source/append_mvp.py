# -*- coding: utf-8 -*-
"""Append Part III (MVP Beta Build Plan) to spec.json, synthesized from the four
code-analysis subagents, and update the exec summary / metadata for the rename."""
import json, io

SPEC = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad\spec.json"
data = json.load(io.open(SPEC, encoding="utf-8"))

def S(title, blocks, is_new=True, part="III"):
    return {"title": title, "part": part, "is_new": is_new, "blocks": blocks}

mvp = []

# III-1 Definition & scope
mvp.append(S("MVP Beta: Definition & Scope", [
 {"type":"p","text":"The MVP Beta is the smallest build that proves the core promise on real homes and real phones: a household picks a micro zone, photographs the honest starting state, works the six steps, photographs the result, and sees a change they could not un-see. Everything that does not serve that first finished zone is deferred. This part is grounded in a full code analysis of the validated v2.4 artifact, summarized in the next section."},
 {"type":"kv","pairs":[
   {"k":"Store listing title","v":"6S Success Home Micro Zones: Organization & Housekeeping (keyword-rich, for App Store and Play search)"},
   {"k":"App name (home screen, spoken)","v":"6S Home Reset (short working brand; a shorter ownable name can be chosen before launch)"},
   {"k":"Beta surface","v":"Apple TestFlight and Google Play closed testing"},
   {"k":"Beta user model","v":"Single user per device. No accounts, no sync, no households."}]},
 {"type":"callout","variant":"idea","label":"The one thing the beta must earn","text":"A tester finishes a real zone in one sitting, with a before and an after photo, and wants to do the next one. That is the whole test."},
 {"type":"h3","text":"The cut line"},
 {"type":"table","headers":["In the beta","Deferred past the beta"],"rows":[
   ["The full zone-reset loop: pick, before photos, AI Sort plan, six steps with substeps, after photos, coach review, a minimal sustain audit","Accounts, sign-in, households, zone-owner assignment"],
   ["A curated set of flagship rooms (see below), not all 20","The full 20 rooms / 114 zones breadth"],
   ["On-device storage of progress and photos","Cloud sync and cross-device continuity"],
   ["AI Sort Plan and Coach Review through a metered server proxy","Subscriptions, paywall, and the free-to-paid wall"],
   ["Product names and purpose in the Zone Kit","Dated price bands, three-way retailer picks, affiliate links"],
   ["A two-tap sustain audit with a timestamp","Push notifications, reminders, scheduling"],
   ["A privacy policy, consent, and permission strings","Before/after share cards, Pro tier, web app"]]},
 {"type":"h3","text":"Curated rooms for the beta"},
 {"type":"p","text":"Shipping all 20 rooms multiplies content QA and product-catalog staleness for no added learning. A curated set of high-traffic flagship rooms proves the loop and sharpens the demo. Recommended starting set (to confirm): Entryway, Kitchen, Primary Bathroom, Primary Bedroom, Home Office, and Laundry. The Entryway leads, matching the book, manual, and video series. The remaining rooms and zones are already authored and switch on without new engineering."}]))

# III-2 what code confirmed & corrected
mvp.append(S("What the Code Analysis Confirmed and Corrected", [
 {"type":"p","text":"Four analysis passes (architecture and port, feature and flow, data and AI, and privacy and compliance) inspected the 1,718-line v2.4 artifact. The content claims hold up exactly; the platform assumptions are the work."},
 {"type":"h3","text":"Every headline count verified against the code"},
 {"type":"table","headers":["Claim","In the code","Match"],"rows":[
   ["20 room types","20","Yes"],["114 micro zones","114","Yes"],["97 sourced products","97","Yes"],
   ["1,812 zone-product mappings","1,812 (Core 402, Recommended 288, Conditional 1,122)","Yes"],
   ["291 retail picks","291 (97 products x 3 tiers)","Yes"],
   ["684 6S activities","684 (114 x 6, engine-generated)","Yes"],
   ["3,062 generated substeps","3,062 (3 to 7 per activity, verified by running the engine)","Yes"]]},
 {"type":"callout","variant":"mistake","label":"Why it is not yet shippable","text":"The app runs only inside the Claude artifact host. Two dependencies must be replaced before a standalone beta: persistence goes through window.storage (an injected key-value store, not device storage), and the AI call is a fetch to the Anthropic API with no key, relying on the host to inject credentials. A shipped binary must never embed the key."},
 {"type":"h3","text":"Corrections and defects to fix in the port"},
 {"type":"table","headers":["Finding","Detail","Action for the beta"],"rows":[
   ["Runtime storage dependency","window.storage plus a chunked photo-write probe that exists only to survive the artifact quota","Replace with device storage; delete the chunking and probe layer entirely"],
   ["Unauthenticated AI call","fetch to the Anthropic API with no key, no version header","Route through a server proxy that holds the key; see the decoupling workstreams"],
   ["Stale model id","claude-sonnet-4-6, max_tokens 1000, which is tight enough to force an elaborate truncation-repair layer","Confirm and set the current model at build time; raise the token cap so responses stop truncating"],
   ["The one genuine catalog gap","Deep Drawer Bin Set (product index 26) maps to no zone, though the Straighten engine has drawer logic","Map it to the drawer zones, or drop it for the beta"],
   ["Five unmapped method tools","Red-tag kit, reset timer, before/after photo card, audit card, QR label kit are catalog items with no zone surface","Expected; these are system tools, not zone products. No action."],
   ["Items-released stat omits relocate","The dashboard totals donate plus discard only, though all three tallies are captured","Fix the stat or relabel it"],
   ["One-tap photo delete","The lightbox deletes a photo with no confirmation","Add a confirm step; home photos are precious to testers"],
   ["Substeps imply gating but do not gate","Checkable substeps look required but do not affect step completion","Clarify the affordance so testers are not confused"],
   ["Rebrand not applied","The UI still reads 6S Success Home Edition","Apply the new store title and app name"]]}]))

# III-3 decoupling workstreams
mvp.append(S("The Two Decoupling Workstreams", [
 {"type":"p","text":"These two pieces of work turn the artifact into an app. They are the critical path; nothing else in the beta can be tested until they land."},
 {"type":"h3","text":"1. Persistence, off the artifact host"},
 {"type":"bullets","items":[
   "Keep the existing storage interface (the get, set, delete wrappers and the save-photo call) so the screens do not change.",
   "Back it with device storage: structured data (home, progress, owned gear) in SQLite or a key-value store, and photos written to the file system as files, with the record holding only a file URI.",
   "Delete the chunking, size-probing, and session-only fallback layer. Native storage has no artifact quota, so that entire subsystem retires.",
   "Collapse the current split (photo ids in progress, data-urls in local state, session photos in memory) into a single photo record with a URI. This removes the app's most fragile code."]},
 {"type":"h3","text":"2. AI, through a thin server proxy"},
 {"type":"bullets","items":[
   "Stand up a small backend endpoint that holds the API key and forwards the Sort Plan and Coach Review calls. The app calls the proxy, never the model directly. No key ships in the binary.",
   "Use an API configuration that is zero-retention and not used for training, and document it. This is both a compliance gate and a marketing asset.",
   "Meter per user or per device so a free beta cannot run up unbounded cost (a hard cap on analyses per tester is enough for the beta).",
   "Confirm the current model and raise the token cap at build time; keep the JSON contracts and the tolerant parser, which port as-is.",
   "Keep AI optional: the app already works with AI disabled, so if the proxy is down the loop still completes on the static plan."]},
 {"type":"callout","variant":"tip","label":"What ports for free","text":"The content datasets, the instruction engines, the AI prompts and JSON contracts, the truncation-repair parser, and all component logic carry over with little change. The rebuild is concentrated in storage, the AI transport, camera and image handling, styling, and navigation."}]))

# III-4 port plan
mvp.append(S("Port Plan & Module Structure", [
 {"type":"p","text":"Target stack: a local-first Expo / React Native app. The business logic and content move over intact; the web-platform pieces are swapped for native equivalents."},
 {"type":"table","headers":["Concern","Current (web artifact)","Native replacement"],"rows":[
   ["Styling","Inline web style objects (100vh, sticky, grid, box-shadow, cursor)","StyleSheet, flexbox only, Text components, native shadow and elevation"],
   ["Storage","window.storage chunked key-value","SQLite or key-value plus file system for photos"],
   ["Camera and photos","file input with capture attribute","expo-image-picker and expo-camera"],
   ["Image decode and compress","createImageBitmap, FileReader, canvas toDataURL","expo-image-manipulator (resize and JPEG quality)"],
   ["AI transport","keyless fetch to the model API","fetch to the app's own proxy"],
   ["Modals","fixed-position div overlays","native Modal"],
   ["External buy links","anchor with target blank","Linking or an in-app browser"],
   ["Navigation","a hand-rolled screen-state machine","keep the state machine for the beta, or adopt a router"]]},
 {"type":"p","text":"Recommended module layout: data (rooms, products, steps, content engine), theme (tokens and styles), services (storage, photos, ai), state (a small store for home, progress, gear), navigation, components, and screens, with App reduced to a provider and a navigator. Add TypeScript and a top-level error boundary before the beta; the artifact has neither."},
 {"type":"callout","variant":"mistake","label":"Build blocker to clear first","text":"window.storage is undefined outside the artifact host, so an unported build white-screens on first render. Replacing storage is task one; standing up the AI proxy is task two."}]))

# III-5 backlog
mvp.append(S("Build-Ready Feature Backlog", [
 {"type":"p","text":"Scoped to the smallest build that delivers the zone-reset loop convincingly. MUST is in the beta, NICE ships only if cheap, CUT or DEFER is out."},
 {"type":"table","headers":["Feature","Call","Note"],"rows":[
   ["Setup, room and zone navigation","MUST","Entry to the whole loop"],
   ["Dashboard next-up prompt and progress","MUST","Orientation and momentum; cheap"],
   ["Zone runner: mission, six steps, substeps, done and undo","MUST","This is the product; already solid"],
   ["Before and after photo galleries","MUST","Half the payoff and the AI input"],
   ["Persistence with real device storage","MUST-FIX","Replaces the artifact dependency; task one"],
   ["In-step product chips (name and purpose only)","MUST","Named in the loop; low maintenance"],
   ["AI Sort Plan and Coach Review via proxy","MUST, conditional","The headline differentiator; ships only with a working authenticated path, else degrades to the static plan"],
   ["Minimal sustain audit (two taps plus timestamp)","NICE","Cheap; closes the 6S story; defer reminders"],
   ["Room briefs, expert tips, game-plan sessions","NICE","Narrative depth; not required to finish a zone"],
   ["Out-the-door tally and items-released stat","NICE","Motivational; fix the relocate omission if kept"],
   ["Full three-way sourcing: prices and retailer links","DEFER","High maintenance and staleness; beta shows names and purpose only"],
   ["Full 20 rooms / 114 zones","DEFER","Curate to the flagship rooms for the beta"],
   ["v1 photo migration code","CUT","No legacy users in a fresh beta"],
   ["Accounts, households, sync, subscriptions, notifications","DEFER","Out of beta scope"]]}]))

# III-6 compliance
mvp.append(S("Beta Compliance & Privacy Gates", [
 {"type":"p","text":"The sensitive asset is photos of the inside of people's homes, which can contain faces, children, mail, and medication, and which are sent to an AI provider on request. These gates are non-negotiable before a real tester captures a real photo."},
 {"type":"h3","text":"P0, before any real home photo enters the beta"},
 {"type":"bullets","items":[
   "Remove the client-side unauthenticated model call; route AI through a server proxy on a zero-retention, no-training configuration. No key in the binary.",
   "Ship a privacy policy and terms, linked in-app and in both store listings, naming the AI provider, stating that photos leave the device on request, retention is none or short, and data is never used for training.",
   "Add first-run consent and a pre-send notice on the AI buttons (your photo will be sent to our AI provider for analysis). The artifact has no privacy copy at all today.",
   "Add native camera and photo-library permission usage strings with honest, specific text.",
   "Encrypt photos at rest in the native shell; the AI call is already HTTPS."]},
 {"type":"h3","text":"P1, required to pass store review"},
 {"type":"bullets","items":[
   "A data-deletion path that also covers any server-retained copy; keep the existing local wipe and label it clearly.",
   "A data-safety form and privacy nutrition label declaring Photos and User Content, shared with a third party for AI processing, no tracking (only if that stays true).",
   "Liability disclaimers for the cleaning-chemistry guidance and for the AI hazards-spotted list: informational only, not a safety inspection, follow product labels.",
   "Runtime validation of AI JSON (clamp the score and clutter values, default the arrays) before render."]},
 {"type":"callout","variant":"note","label":"Chemical and hazard content carries liability","text":"The content gives specific home-chemistry instructions (never mix cleaners, chlorine away from ammonia, degrease before sanitize) and the AI emits a hazards-spotted list. Both are responsible, but if the AI misses a real hazard a user may rely on it. Prominent disclaimers are required, and the app must not present itself as a safety inspection."}]))

# III-7 acceptance
mvp.append(S("Acceptance Criteria", [
 {"type":"p","text":"The beta is done when all of the following are demonstrably true on a physical device."},
 {"type":"h3","text":"Functional"},
 {"type":"bullets","items":[
   "A tester completes the full loop for at least one zone: before photos, an AI Sort plan, six steps, after photos, a coach review, and a sustain audit.",
   "Progress and photos survive an app restart and airplane mode; the loop works offline except for the two AI calls.",
   "The AI calls succeed through the proxy with no key in the binary, and fail gracefully to the static plan when unavailable.",
   "Data wipe removes all local photos and progress, and the deletion path covers any server copy."]},
 {"type":"h3","text":"Quality and compliance gates"},
 {"type":"bullets","items":[
   "Crash-free across the curated rooms; no white screen on cold start.",
   "Camera and photo permission prompts appear with correct strings; denial is handled.",
   "Privacy policy, consent, pre-send notice, and liability disclaimers are present and linked.",
   "No secret in the binary; AI JSON is validated before render; the rebrand is applied throughout."]}]))

# III-8 beta plan
mvp.append(S("Beta Test Plan & Timeline", [
 {"type":"p","text":"Recruit testers from the audience the content ecosystem already reaches (the book, the manual, and the video series), which is also the app's per-zone acquisition funnel."},
 {"type":"table","headers":["Track","Plan"],"rows":[
   ["Apple","TestFlight internal first (up to 25), then external (beta review required)"],
   ["Google Play","Closed testing; a personal developer account must run 12 or more testers for 14 continuous days before production, so recruit that cohort regardless"],
   ["What to measure","Activation (a first zone finished with before and after photos), AI attach rate (zones that use a Sort plan), and qualitative feedback on whether testers want the next zone"],
   ["Instrumentation","Privacy-respecting event logging for the loop milestones only; no cross-app tracking"]]},
 {"type":"callout","variant":"note","label":"Timeline is an estimate to validate","text":"A lean beta subset (port and local storage, AI proxy, camera and image swap, styling, the curated rooms, and the P0 compliance items) is plausibly a 5 to 7 week effort with one experienced React Native developer plus part-time backend, shorter than the full v1.0 roadmap because accounts, sync, subscriptions, and notifications are deferred. Confirm against real team capacity; store review and closed-testing gates add calendar time beyond build time."}]))

# III-9 deferred
mvp.append(S("Explicitly Deferred Beyond the Beta", [
 {"type":"p","text":"Stated plainly so the beta line is unambiguous and scope creep has a clear boundary."},
 {"type":"bullets","items":[
   "Accounts, households, member invites, and zone-owner assignment",
   "Cloud sync and cross-device continuity",
   "Subscriptions, the paywall, and the free-to-paid wall",
   "Push notifications, reset reminders, and audit scheduling",
   "The full 20 rooms and 114 zones, switched on after the curated set proves out",
   "The full product catalog depth: price bands, three-way retailer picks, and affiliate links",
   "Before and after share cards, the Pro tier, a web app, and non-US markets"]}]))

# attach as a new unit
data.setdefault("units", []).append({"unit": "U13", "sections": mvp})

# update the exec summary to acknowledge Part III and the rename
for u in data["units"]:
    for s in u.get("sections", []):
        if s.get("title") == "Executive Summary":
            s["blocks"].insert(2, {"type":"p","text":"Part III is new in this revision: an MVP Beta build plan grounded in a full code analysis of the v2.4 artifact. It defines the smallest shippable beta of the app, provisionally titled 6S Success Home Micro Zones: Organization & Housekeeping for the stores, that proves the core zone-reset loop on real homes. The code analysis confirmed every headline content count exactly and identified the two dependencies that must be replaced to leave the artifact host."})

io.open(SPEC, "w", encoding="utf-8").write(json.dumps(data, indent=1, ensure_ascii=False))
print("appended Part III: %d sections" % len(mvp))
print("total units:", len(data["units"]))
