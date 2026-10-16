# Photos API: before/after storage and method-grounded analysis

**Owner:** software-engineer (build), security-auditor (release gate), product-manager (the analysis contract).
**Status, 2026-10-15:** backend built and tested locally; **not deployed.** Frontend built, tested against the local backend, deliberately not linked. Turning both on is one step: `OWNER-ACTIONS.md` item 22.
**Code:** `photos/` (service), `ops/tests/test_photos_service.py` (37 end-to-end checks over real HTTP); `site/photo-check.html` + `site/assets/js/photo-check.js` (frontend); `ops/build_photo_check_data.py` + `ops/tests/test_build_photo_check_data.py` (zone picker data).

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
code changes, because neither had a frontend yet to be exploitable through.
One is now closed, not just documented: model output fields (`summary`,
item/step text) are length-clipped but not HTML-sanitised, and
`site/photo-check.html` + `site/assets/js/photo-check.js`, built 2026-10-15,
is the first code that renders them. Re-verified directly this cycle against
the committed file, not assumed from the build commit's own claim: every
model-controlled field in `photo-check.js` renders through `textContent`
(12 call sites), and the file's one `innerHTML` assignment only clears a
container (`container.innerHTML = ""`) before those `textContent` calls run,
never assigns untrusted data to it. The second finding is still open and is
unrelated to the frontend: `nginx-location.conf`'s `access_log off` only
covers the inner hop, so Nginx Proxy Manager's own access log (not yet
created) may still record paths carrying session ids.

Every fix above is proved fail-then-pass directly in
`ops/tests/test_photos_service.py` (33/33 checks): each new case was run
against the pre-fix code first and confirmed to fail the way the finding
describes, then confirmed to pass after.

## Found and fixed, 2026-10-16: a lost-upload race, not covered by the lanes above because `photos/` has no cold-read lane yet

Not found by either security pass above; both reviewed the code adversarially
for attacker-triggered gaps, and this is a correctness defect under ordinary,
honest use. `photos/*.py` is also outside every lane `ops/cold_read_ledger.py`
sweeps (`ops/*.py`, `ops/*.js`, `site/assets/js/*.js`,
`mobile/quest-app/lib/*.js`), so nothing had read these four files end to end
since the security passes. Read directly this cycle after the standing
backlog and cold-read queues both came back fully exhausted.

`Store.add_photo`/`delete_photo`/`save_analysis` each did read-modify-write
on one session's `meta.json` with no lock. `ThreadingHTTPServer` gives every
request its own thread, so two overlapping requests on the same session (a
before and an after photo uploaded back to back is the ordinary case, not an
edge case) can both read the file before either writes it back; the second
write then silently replaces the first writer's new entry. The `.jpg` itself
still lands on disk, orphaned and unreferenced, while the caller who
uploaded it was already sent `201`. Proved directly against the pre-fix
code with a forced, deterministic interleave (not hoping two real threads
collide by timing luck): both uploads returned `201`; only one id appeared
in the session's photo list afterward.

**Fixed.** One re-entrant lock per session (`Store._lock_for`, created only
once a session directory is confirmed to exist, so a flood of guessed or
invalid session ids cannot grow the lock table) now wraps every read through
write for that session end to end, replacing the old pattern where `open()`
did its own separate read-write cycle before the caller's own mutate-and-
write ran unguarded. Re-proved fail-then-pass in
`ops/tests/test_photos_service.py` (now 37/37): the new cases force a second
request to actually block mid-`open()` while the first still holds the lock
(not merely "happened to pass"), then confirm both uploads are kept.

`site/photo-check.html` + `site/assets/js/photo-check.js` take a before/after
photo and render the answer, calling the contract above exactly (verified
directly against a locally run `photos/server.py`, not just read from this
file: session create, photo PUT, analyze, delete, and the 404-on-bad-token
shape were each exercised with curl before the client code was written).
Zone data comes from `site/assets/js/photo-check-zones.js`, generated by
`ops/build_photo_check_data.py` (registered in `preflight.py`'s
`GENERATOR_OWNERSHIP_CHAIN`) by importing `photos/methodology.py` directly,
so the picker can never offer a slug `GET /v1/zones` would reject.

**Deliberately not linked from anywhere, not in the sitemap or feed**
(`<meta name="robots" content="noindex, nofollow">`, which
`ops/build_seo.py`'s own `scan_extra_pages()` already treats as the signal to
exclude a page, the same mechanism the Google verification file uses). The
page detects whether the API answers `GET /v1/health` before showing the
upload form at all; today, undeployed, that call fails and the page shows
"this feature is not live yet" with a link to the zone pages instead of a
broken form, so a direct hit on the URL (nothing currently links to it) does
not look like a dead feature.

**Turning it on is now the same single step as the backend**: deploy
`photos/` (`OWNER-ACTIONS.md` item 22), then remove the noindex/nofollow line
and link the page in (the quest footer's "no email needed" line is the
obvious spot). Nothing else needs building first.

## Not yet built

- An MCP tool wrapping these calls for Claude users (`mcp/` is itself undeployed, D-028).
- Before/after pairs feeding `ops/video_cleanalong.py`: a pair a household chooses
  to share would need explicit, separate consent, and nothing here publishes anything.
