# 6S Success Backup and Restore

> Concrete backup policy and restore procedure, as distinct from `DISASTER-RECOVERY.md`, which handles catastrophic loss more broadly. Required by `CLAUDE.md` section 56. Written 2026-08-24 from the architecture as it actually exists today, not from a template. Where a status below is UNKNOWN, that is the honest answer, not a placeholder waiting to be filled with something reassuring.

## 1. What actually needs backing up, given the current architecture

The site is static files served from a pulled Docker image; there is no application database. That materially shrinks what "backup" has to mean here, compared to a system with a live datastore. What exists today:

| Data | Where it lives | Backup status |
|---|---|---|
| Site content, code, and every operating document (this one included) | This Git repository, on GitHub | **Covered.** Every commit is retained; GitHub's own infrastructure is the off-host copy. A local working copy alone is not a substitute for this, per section 63 of `DISASTER-RECOVERY.md`. |
| The Docker image actually running in production | `ghcr.io/klingdom/6s-success`, built from this repo by CI | **Covered by reproducibility, not by a snapshot.** Any tagged image can be rebuilt from the exact commit that produced it. Older tags remain pullable unless manually deleted from the registry. |
| VPS runtime configuration (compose file, reverse proxy rules, port assignment) | Documented in `DEPLOY-VPS.md`, applied by hand on the Hostinger VPS | **Traceable to Git, not independently backed up.** The documented state should be sufficient to reconstruct the host, but this has not been tested end to end (see section 3). |
| Stripe products, prices, and transaction history | Stripe, external | **Not this system's backup to make.** Stripe is the authoritative system of record for payments; `ops/stripe_catalog.py` keeps the local catalog in sync with it, not the other way around. |
| Mailbox (`support@6s-success.com` and related) | Hostinger-hosted mail | **UNKNOWN.** Whatever backup Hostinger provides for hosted mail has not been verified from inside this project. |
| Email subscriber list | Not yet capturing anyone; the signup form is withdrawn pending issue #15 | **Not applicable yet.** Once a Listmonk instance is live and collecting real subscribers, its export/backup needs to be added to this table before it holds data worth losing. |
| `ops/inbox-state.json`, `ops/experiments.json`, and similar operational state files | This Git repository | **Covered**, same as content, with one caveat: `ops/inbox_agent.py` deliberately does not persist the full text of owner or customer emails into this file, only classification metadata, so it is not a substitute for the mailbox itself. |

## 2. Retention

Git history is retained indefinitely by default; nothing in this project's workflow deletes commits or history. Registry image tags persist until someone manually prunes them; no automatic expiry is currently configured.

## 3. What has never actually been tested

**No restore has been tested end to end.** Section 39 of `CLAUDE.md` is explicit that a successful backup job is not proof of recoverability, and the honest state here is that "the VPS can be rebuilt from `DEPLOY-VPS.md`" is a claim, not a demonstrated fact. Nobody has provisioned a fresh host and confirmed the site comes back up following that document alone.

This is a real gap, not a rhetorical one. If a restore test is undertaken, record the result (what worked, what the document was missing, how long it took) in `ops/NIGHTLY-LOG.md` and update this section from UNKNOWN to a dated, verified status.

## 4. Restore procedure, as far as it is currently known

1. **Code and content:** clone this repository from GitHub. Nothing else is required to reconstruct the site's source.
2. **Running container:** pull the last known-good tag from `ghcr.io/klingdom/6s-success` and start it per `DEPLOY-VPS.md`. If that tag is unavailable, rebuild it by checking out the corresponding commit and running the same GitHub Action locally.
3. **Reverse proxy and port binding:** re-apply the configuration documented in `DEPLOY-VPS.md` section covering Nginx Proxy Manager and the 8973 port assignment. This step is the one most dependent on tribal knowledge rather than an automated script, and is the best candidate for the first restore test.
4. **Stripe:** nothing to restore; it is the source of truth on its own.
5. **Mail and subscriber data:** currently outside this project's ability to restore, since backup status for both is UNKNOWN (section 1). Do not claim otherwise until verified.

## 5. Access

Restoring code requires GitHub repository access. Restoring the running container requires Hostinger Docker Manager access. Neither is available to an autonomous session with the sandboxed network described in `DAILY-LOOP.md` section 5; both currently require Phil.

## 6. Read with

- `DISASTER-RECOVERY.md`, for total loss scenarios beyond routine restore
- `DEPLOY-VPS.md`, the procedure section 4 above depends on
- `RUNBOOK.md`, day-to-day operational procedures
- `SECURITY.md`, credential and access handling
