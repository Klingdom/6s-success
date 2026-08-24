# 6S Success Deployment

> Canonical short reference for how a change reaches production. Required by `CLAUDE.md` section 56. The detailed procedures already exist in `DEPLOY.md` and `DEPLOY-VPS.md`; this file is the index that ties them together and states current reality, not a third copy of the same steps.

## 1. The pipeline as it actually runs

```
push to main  ->  GitHub Action builds the image  ->  ghcr.io/klingdom/6s-success:latest
                                                            |
                                          Hostinger Docker Manager pulls it (manual Redeploy click)
```

The production host pulls a finished image. It does not clone this repository and it does not build anything, which means zero credentials touch the VPS. See `DEPLOY-VPS.md` for why this shape was chosen over the alternatives.

**The one step no autonomous session can perform is the Redeploy click** in Hostinger's Docker Manager UI. Every cycle that pushes a change must say so plainly in `ops/NIGHTLY-LOG.md`: the image is built and published, and it is awaiting that click, not already live. Do not infer "deployed" from "CI succeeded."

## 2. Order of operations that must not be skipped

1. Make the change.
2. Re-run the four gates (`ops/audit_pages.py`, `ops/fix_dashes.py --check`, `ops/fingerprint_assets.py --check`, `content/manual/source/validate.py`).
3. **If anything under `site/assets` changed, run `ops/fingerprint_assets.py` before pushing.** CI refuses to publish otherwise, and this has cost a build before: see the 2026-08-24 nightly log entry describing a build silently red across five pushes because this order was missed once.
4. If a price or product changed, run `STRIPE_ALLOW_LIVE=1 python ops/stripe_catalog.py --apply` so Stripe, the catalog, and the structured data cannot drift apart.
5. Push to `main`.
6. **Poll the actual GitHub Actions run conclusion**, not just that the push succeeded. A green push and a green build are different facts; only the second one means the image is really in the registry. See issue #25.
7. If a page was added or rewritten, run `ops/indexnow.py --submit`. This currently cannot complete from most autonomous sessions; see section 3.

## 3. Known limitation: verifying the live result

Most autonomous sessions run in a sandboxed network that returns a policy 403 for `6s-success.com`, `api.stripe.com`, and `api.indexnow.org`. That means a session can confirm the image built and published, but not that the live site actually serves it, that IndexNow received the submission, or that a Stripe change took effect against the real account. This is tracked as issue #22 and is a process gap, not something to silently route around: the honest state is "pushed and built, live status unverified this session," never "deployed."

## 4. Rollback

A rollback is a pull of the previous image tag in Hostinger's Docker Manager, the same manual action as a forward deploy. Because the host only ever pulls a tagged image and never builds from source, the previous tag is always a known-good target. See `DISASTER-RECOVERY.md` for what to do if the previous tag itself is unavailable or the host is lost entirely.

## 5. Read with

- `DEPLOY.md`, the original static-site container setup
- `DEPLOY-VPS.md`, the Hostinger-specific pipeline, port assignment, and the shared-VPS constraints (this host also runs Ledgerium AI and Compassion Benchmark)
- `RUNBOOK.md`, routine operational procedures
- `DISASTER-RECOVERY.md`, what to do when deployment fails catastrophically rather than routinely
