# -*- coding: utf-8 -*-
"""Append Part IV (Usability, Data & Visualization) to spec.json, synthesized from
the seven-discipline MVP review panel (59 findings)."""
import json, io

SPEC = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad\spec.json"
data = json.load(io.open(SPEC, encoding="utf-8"))

def S(title, blocks, part="IV"):
    return {"title": title, "part": part, "is_new": True, "blocks": blocks}

p4 = []

# IV-1 method + headline
p4.append(S("Review Panel: Method & Headline Findings", [
 {"type":"p","text":"Seven disciplines reviewed the running MVP prototype and this spec: product management, software quality assurance, front-end, back-end, marketing, customer success, and support. They produced 59 findings against three themes the product owner asked to improve: usability, data collection, and visualization. This part turns the convergent findings into committed spec changes."},
 {"type":"stats","items":[{"num":"7","label":"disciplines"},{"num":"59","label":"findings"},{"num":"27","label":"high severity"},{"num":"3","label":"themes"}]},
 {"type":"callout","variant":"mistake","label":"The five things every discipline circled","text":"1) The beta emits zero analytics events, so its own test questions are unanswerable. 2) The before/after transformation, the whole payoff, is captured but never shown to the user. 3) AI is unreachable by testers (endpoint off by default), so the differentiator and its attach rate go untested. 4) Every failure dies in a 3.4-second toast with nothing captured. 5) There is no in-app help, feedback, or diagnostic path, and home photos mean testers cannot even screenshot a bug."},
 {"type":"p","text":"None of these are deep rebuilds. They are the difference between a beta that demos and a beta that learns. The sections below are organized by the three themes; a prioritized do-next list closes the part."}]))

# IV-2 usability
p4.append(S("Usability Improvements", [
 {"type":"p","text":"Changes that make the app clearer, more motivating, and safer to use, drawn from the panel and ranked by severity."},
 {"type":"table","headers":["Change","Why","Severity"],
  "rows":[
   ["Guide first-run to one fast-win zone","First-run drops the tester into a 37-zone program instead of steering to a single finished zone. Onboarding should pick one high-payoff zone and walk it end to end so value lands in the first sitting.","High"],
   ["Gate completion on a before AND an after photo","A zone can currently be marked done with only an after photo, which breaks the activation definition. Require one of each.","High"],
   ["Show the before/after reveal on completion","The transformation is stored but never shown paired. On completion, present a before/after compare plus the items-released count and a Start-next-zone button. This is the conversion hinge from one zone to the next.","High"],
   ["Make AI reachable, or show an honest off-state","AI is gated behind a manual endpoint no tester will set, so the flagship feature reads as a dead button. Ship the beta with the proxy pre-configured, and when no endpoint exists render an explicit off-state rather than an actionable dead-end.","High"],
   ["Replace toast-only failures with persistent, recoverable error states","AI, photo decode, and storage all fail into a 3.4-second toast (AI with a silent 60-second wait, no cancel, no retry). Add persistent failure states with Retry and Cancel, and honest copy.","High"],
   ["Add in-app help, feedback, and a photo-free diagnostic export","There is no way to report a problem in-app, and because the asset is home photos, testers cannot safely screenshot a bug. Add a Report-a-problem path and a redacted diagnostic export.","High"],
   ["Add a top-level error boundary and clamp AI JSON before render","A render throw white-screens with nothing logged; an out-of-range AI score renders as 7/5. Add a recovery boundary and validate AI values (1 to 5, default arrays).","Medium"],
   ["Fix the honest-storage notice and the in-memory fallback message","When photos run in memory the app still promises Stays on this device. Show the true state.","Medium"],
   ["Accessibility pass","Status is carried by color alone, icon controls are unlabeled, and there is no dynamic-type or contrast provision. Add labels, non-color status, larger tap targets, and scalable text.","Medium"],
   ["Clarify substep affordance","Checkable substeps look required but do not gate step completion. Make the affordance read as optional guidance, or gate on them, but not the ambiguous middle.","Medium"]]},
 {"type":"callout","variant":"note","label":"A data-integrity defect the panel caught in the build","text":"The prototype's items-released stat sums donate, discard, AND relocate, which inflates the north-star. Relocate is moved-elsewhere, not released. Pin the definition to donate plus discard, and track relocate separately. This corrects the earlier code-analysis note, which had it the other way."}]))

# IV-3 data collection
p4.append(S("Data Collection", [
 {"type":"p","text":"The beta must answer whether a household reaches a finished zone with before and after photos and then keeps going. Today it captures none of that. Everything below inherits the existing privacy contract: counts, enums, small integers, and booleans only; no photo, home name, room name, free text, or full endpoint URL ever enters telemetry."},
 {"type":"h3","text":"Beta instrumentation, on device"},
 {"type":"p","text":"Implement the loop-milestone events in the beta build itself, append-only and privacy-safe, rather than deferring them to the backend. This makes activation, AI attach, and step drop-off computable from a tester's device from day one."},
 {"type":"bullets","items":[
   "setup_complete, zone_started, before_photos_added, sort_plan_requested, step_completed (property: step, one of the six S), after_photos_added, coach_review_received, zone_completed, audit_action (property: result)",
   "Attach the quality signals the AI already returns: clutter_before on sort_plan_requested; score_after and meets_standard on coach_review_received; improvement_delta on zone_completed",
   "zone_completed carries items_released (donate plus discard), items_relocated (separate), and session_minutes (measured elapsed time, not the budget estimate the dashboard uses today)",
   "A referral_source captured at setup (privacy-respecting, self-reported or a first-party deep-link tag) so the content funnel can be measured"]},
 {"type":"h3","text":"Health and reliability signals (new event family)"},
 {"type":"p","text":"A second family, same privacy rules, so failures are visible and tickets can be triaged. Without these, a tester hitting repeated AI errors looks identical to a happy one."},
 {"type":"table","headers":["Event","Fires when","Carries"],
  "rows":[
   ["ai_call_failed","A Sort plan or coach review fails","error_class: no_endpoint | timeout | network | http_error | empty_reply | parse_failure"],
   ["ai_latency_ms","Any AI call returns","latency (integer)"],
   ["storage_mode","Once at boot","mode: persistent | session_only"],
   ["storage_write_failed","A progress, gear, or photo write is rejected","surface"],
   ["photo_decode_failed","An image cannot be decoded","(count only)"],
   ["json_repair_invoked","The truncation-repair path runs","(count only)"],
   ["app_error","The error boundary catches a throw","error_class, screen"]]},
 {"type":"h3","text":"Schema and pipeline changes"},
 {"type":"bullets","items":[
   "Store an append-only per-zone audit log (timestamp, result) instead of a single overwritten drift flag, so Sustain retention and the two-consecutive-drift redesign rule are computable",
   "Capture the Sustain owner, reset trigger, and chosen cadence (weekly or monthly), and drive the audit-due banner off the chosen cadence rather than a hardcoded 7 days",
   "Stamp the catalog version on device and on relevant events so sourcing refreshes are traceable",
   "The AI proxy meters and logs per device or user (request count, latency, token cost, model), and pins the model server-side rather than trusting the client",
   "A small on-device event client with an offline queue and a batched, PII-free flush to a privacy-respecting analytics store",
   "Redaction rule: the AI endpoint URL may carry a token, so diagnostics and telemetry record at most its hostname, never the path or query"]}]))

# IV-4 visualization
p4.append(S("Visualization", [
 {"type":"p","text":"Two audiences: the user, who needs to feel momentum and see the change; and the team, who need discipline dashboards to run the beta. The prototype has the four signature user visualizations (progress rings, the six-segment step spine, zone-dot strips, stat tiles) but no completion reveal and no team views at all."},
 {"type":"h3","text":"User-facing"},
 {"type":"bullets","items":[
   "The before/after compare on zone completion: the single most motivating view in a habit product, and it is currently absent",
   "Items released as a hero stat, defined consistently with the metric and the future share card (donate plus discard)",
   "A home-level momentum view (zones finished, streak, time this week) richer than the current three tiles, since keeping is the point",
   "An honest time visualization based on measured minutes, replacing the budget-derived estimate"]},
 {"type":"h3","text":"Team dashboards (define now, build with the backend)"},
 {"type":"table","headers":["Dashboard","Owner","Shows"],
  "rows":[
   ["Six-S activation funnel","Product","install to setup to zone_started to before to each step_completed(step) to after to coach to zone_completed; where testers drop"],
   ["Household health and cohorts","Customer success","thriving / steady / at-risk banding from activation, recency, audit-holding ratio, and AI-error rate, plus a D0/D7/D28 cohort retention grid on audit_action"],
   ["Support and reliability","Support","AI failure rate by error_class, session-only storage incidence, photo-decode rate, crash-free rate, and self-reported tickets by loop stage, sliced by build"],
   ["Growth and funnel","Marketing","referral_source to install to activation by channel, share-card generation and share-to-install, and the 1:1 content-to-zone deep-link path"],
   ["Home improvement","Product / CS","before-to-after improvement_delta and meets_standard rate: the truest proof the product works"]]},
 {"type":"callout","variant":"tip","label":"One shared foundation","text":"All five dashboards read from the same two event families over the same aggregation layer. Build the pipeline once (Data Collection above); each discipline gets a view, not a separate integration. Every view is aggregate-only, with no per-household drill-down, so team data stays private."}]))

# IV-5 corrections
p4.append(S("Corrections to Earlier Parts", [
 {"type":"p","text":"The review reconciled the spec against the running build and against itself."},
 {"type":"table","headers":["Item","Correction"],
  "rows":[
   ["Items released definition","Pin to donate plus discard only; relocate is tracked separately as items_relocated. The Part III code-analysis note had this backwards; the build actually over-counts by including relocate."],
   ["AI automatic retry","Part I describes one automatic retry with backoff. The ported prototype does a single attempt with no retry. Treat retry as a build-time requirement not yet present, and reconcile the two."],
   ["Time invested","The dashboard stat is the static budget prorated by steps done, not measured time. Relabel as estimated or, preferably, back it with real elapsed minutes (session_minutes)."],
   ["Error boundary and AI JSON validation","Promote both from aspirational notes to explicit Acceptance Criteria gates: a top-level error boundary must exist, and AI values must be clamped before render."],
   ["Completion definition","Align the code with the Activation metric: a zone requires at least one before and one after photo to count as complete."]]}]))

# IV-6 do next
p4.append(S("Prioritized Do-Next for the Beta", [
 {"type":"p","text":"The deduped, cross-discipline priority order. The first tier is what makes the beta a learning instrument; do it before testers touch real homes."},
 {"type":"h3","text":"Tier 1, before the beta ships"},
 {"type":"bullets","items":[
   "On-device loop instrumentation plus the health and reliability event family",
   "The before/after completion reveal, with completion gated on both photos",
   "AI pre-configured (or an explicit off-state), with persistent, recoverable error states",
   "In-app help, feedback, and a photo-free diagnostic export; a top-level error boundary",
   "Fix items-released to donate plus discard; capture measured session time"]},
 {"type":"h3","text":"Tier 2, during the beta"},
 {"type":"bullets","items":[
   "Guided first-run to one fast-win zone; at-risk and stalled-zone in-app nudges",
   "Append-only audit log with owner, trigger, and cadence; cadence-driven audit-due banner",
   "The five team dashboards on the shared aggregation layer",
   "Accessibility pass; substep affordance clarity; honest storage-mode notice"]},
 {"type":"h3","text":"Tier 3, as the store product forms"},
 {"type":"bullets","items":[
   "On-device before/after share card (photos leave only on an explicit user share) plus deep-link attribution",
   "AI proxy metering, cost logging, and server-pinned model; catalog version stamping",
   "Endpoint validation and a test-connection affordance"]},
 {"type":"callout","variant":"idea","label":"The one-line takeaway","text":"The MVP proves the loop. To make the beta prove the business, instrument the loop, show the transformation, and turn AI on. Everything else is a refinement of those three."}]))

data.setdefault("units", []).append({"unit": "U14", "sections": p4})

# reflect Part IV in the exec summary
for u in data["units"]:
    for s in u.get("sections", []):
        if s.get("title") == "Executive Summary":
            s["blocks"].insert(3, {"type":"p","text":"Part IV is added in this revision: the committed usability, data-collection, and visualization changes from a seven-discipline review of the running MVP (product, QA, front-end, back-end, marketing, customer success, and support). Its headline: the beta must instrument its own loop, show the before/after transformation, and turn AI on, or it will demo without learning."})

io.open(SPEC, "w", encoding="utf-8").write(json.dumps(data, indent=1, ensure_ascii=False))
print("appended Part IV:", len(p4), "sections; total units:", len(data["units"]))
