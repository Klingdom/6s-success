# Photos API: before/after storage and method-grounded analysis

**Owner:** software-engineer (build), security-auditor (release gate), product-manager (the analysis contract).
**Status, 2026-10-14:** built and tested locally; **not deployed.** Turning it on is `OWNER-ACTIONS.md` item 22.
**Code:** `photos/` (service), `ops/tests/test_photos_service.py` (26 end-to-end checks over real HTTP).

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

12 MB per image, 25 megapixels per image (checked from the header before
decode), at most 2 decodes running at once, 2048 px longest side stored, 200
photos per session **and 150 MB per session**, 20 analyses per session per
day **plus 20 per address per hour and 100 across every address per hour**,
10 new sessions per address per hour, and new uploads are refused once the
shared disk has under 1 GB free. All the counters above are **persisted to
disk** (`photos/<data>/rate.json`), not held only in memory.

## Found and fixed in the independent security review before deploy, 2026-10-15

A first pass (same day) found the decompression-bomb gap above (a flat-colour
PNG under 1 MB decoded to over 600 MB of RGB, nearly 3x this container's 256 MB
limit, from a single authenticated upload) and fixed it: image dimensions are
read from the header and checked against `MAX_PIXELS` before the expensive
decode, and a semaphore bounds concurrent decodes. A second, genuinely
independent pass (a different session, deliberately not told about the first
session's own reasoning beyond the code it left behind) then found three more,
all fixed the same day:

1. **Financial DoS.** `ANALYSES_PER_DAY` bounds one session; it does nothing
   against an attacker who just opens more sessions (10/hour/address, cheap)
   or rotates addresses. Each `/analyze` call is a paid vision-provider
   request with no other ceiling. Fixed: `ANALYSES_PER_IP_HOUR` (20) and
   `ANALYSES_GLOBAL_PER_HOUR` (100), independent of session or address, cap
   the actual worst-case spend regardless of how the per-session/per-address
   limits are evaded. This is in addition to, not instead of, the spend limit
   `OWNER-ACTIONS.md` item 22 asks Phil to set at the provider itself.
2. **Disk-exhaustion DoS with a cross-tenant blast radius.** No per-session or
   global disk quota existed; measured, 200 photos/session can reach ~600 MB,
   and 10 sessions/hour/address compounds that to tens of GB/day from one
   address. The shared VPS (`CLAUDE.md` section 36b, D-028) also runs
   Ledgerium and Compassion Benchmark, so filling the disk takes those down
   too, not just this service. Fixed: a 150 MB per-session byte quota (summed
   from each photo's real stored size), plus a hard floor checked before any
   write (`shutil.disk_usage`, refuses once under 1 GB free) that protects
   against disk pressure from any cause, not only this service's own usage.
3. **Rate limits were in-process memory only.** `restart: unless-stopped`
   means a deploy, a crash, or an OOM kill (which finding 2, uncorrected,
   could itself have caused) silently rearmed every limiter, including the
   two above. Fixed: all counters (`Store.allow()`) are now persisted to a
   small JSON file and reloaded on start, proved directly by creating a fresh
   `Store` on the same data directory mid-test and confirming a limit already
   hit stays hit.

Two findings from the same pass were left as a documented risk rather than
code changes, because neither has a frontend yet to be exploitable through:
model output fields (`summary`, item/step text) are length-clipped but not
HTML-sanitised, so whoever builds the `quest.html` photo page **must** render
them as text, never `innerHTML`; and `nginx-location.conf`'s `access_log off`
only covers the inner hop, so Nginx Proxy Manager's own access log (not yet
created) may still record paths carrying session ids.

Every fix above is proved fail-then-pass directly in
`ops/tests/test_photos_service.py` (33/33 checks): each new case was run
against the pre-fix code first and confirmed to fail the way the finding
describes, then confirmed to pass after.

## Not yet built

- The page in the web app (`quest.html`) that takes a photo and shows the answer.
- An MCP tool wrapping these calls for Claude users (`mcp/` is itself undeployed, D-028).
- Before/after pairs feeding `ops/video_cleanalong.py`: a pair a household chooses
  to share would need explicit, separate consent, and nothing here publishes anything.
