# Photos API: before/after storage and method-grounded analysis

**Owner:** software-engineer (build), security-auditor (release gate), product-manager (the analysis contract).
**Status, 2026-10-14:** built and tested locally; **not deployed.** Turning it on is `OWNER-ACTIONS.md` item 22.
**Code:** `photos/` (service), `ops/tests/test_photos_service.py` (24 end-to-end checks over real HTTP).

## What it is for

A household, a phone app, or an AI agent stores a photo of one micro zone
before and after working it, and asks: what should I do next here? The answer
is in the zone's own published terms: which items stray in, which friction is
visible, which of the 17 root causes is likely, which of the six passes to run,
and, for an after photo, which line of the zone's done-looks-like standard is
met.

## The contract

Base URL once deployed: `https://6s-success.com/api/photos`. The machine-readable
contract is `GET /v1/openapi.json`.

| Call | Purpose |
|---|---|
| `POST /v1/sessions` | Create a private session. Returns `session_id` and `token`, **shown once**. |
| `PUT /v1/sessions/{sid}/photos?zone=<zone>&kind=before\|after\|progress` | Store one image. Body is the raw image bytes. |
| `GET /v1/sessions/{sid}/photos` | List. |
| `GET /v1/sessions/{sid}/photos/{pid}` | The stored JPEG. |
| `POST /v1/sessions/{sid}/analyze` `{"photo_id": "...", "compare_to": "<before id>"}` | Analyze. |
| `DELETE /v1/sessions/{sid}/photos/{pid}`, `DELETE /v1/sessions/{sid}` | Delete, immediately. |
| `GET /v1/zones`, `GET /v1/zones/{zone}/method` | Public: the 114 zone ids and each zone's method. |

`zone` is the zone page slug, e.g. `entryway-the-landing-spot`
(= `https://6s-success.com/zones/entryway-the-landing-spot`). Every session
route needs `Authorization: Bearer <token>`.

## Privacy, as code rather than promise

- No accounts. A session is a capability; only the token's SHA-256 is stored.
- Every upload is decoded and re-encoded: EXIF, **including GPS**, is gone. Non-images are refused.
- Nothing is public, nothing is listed across sessions, and a wrong token looks exactly like a missing session.
- Delete is immediate. Sessions untouched for 90 days are purged at start-up.
- No request log on the route (paths carry session ids), and the service logs nothing per request.
- Photos are sent to the vision provider **only** when an analysis is requested, and that provider is named in every response (`provider`).

## Grounding: the model observes, the method instructs

The vision model may describe what it sees. It may not invent the method.
`photos/analyze.py` keeps a step only if it names one of the six passes, keeps a
root cause only if it is one of the 17 in `ops/root_causes.py`, and when a step
points at a surface it attaches **the published method for that surface**, not
the model's wording. Everything dropped is counted in `dropped_as_outside_method`.

With no vision key configured, analysis returns `"image_analyzed": false` and
the zone's published steps. It never implies it looked.

## Limits

12 MB per image, 2048 px longest side stored, 200 photos per session, 20
analyses per session per day, 10 new sessions per address per hour.

## Not yet built

- The page in the web app (`quest.html`) that takes a photo and shows the answer.
- An MCP tool wrapping these calls for Claude users (`mcp/` is itself undeployed, D-028).
- Before/after pairs feeding `ops/video_cleanalong.py`: a pair a household chooses
  to share would need explicit, separate consent, and nothing here publishes anything.
