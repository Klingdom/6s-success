# Deploying 6S Success to the Hostinger VPS

Updated 2026-08-19 from `ops/NIGHTLY-LOG.md`: the package is public, the compose
is deployed, and DNS points at the VPS. One step remains, the proxy host entry,
described at the bottom.

## How this works, and why

The production host **pulls a finished image**. It does not clone this
repository and it does not build anything.

```
push to main  ->  GitHub Action builds the image  ->  ghcr.io/klingdom/6s-success:latest
                                                            |
                                          Hostinger Docker Manager pulls it
```

That shape was chosen deliberately over the two alternatives:

| Approach | Why not |
|---|---|
| VPS clones the private repo | Needs a deploy key on the host, or a token pasted into the Docker Manager UI where it sits in a web panel forever. More credentials, more to rotate. |
| VPS builds from source | The host does compile work it does not need to do, and a deploy becomes a rebuild of a moving branch rather than a pull of a known tag. Harder to roll back. |
| **Pull a published image** | The host needs no repository access at all. A deploy is a pull of a specific tag, and a rollback is a pull of the previous one. |

The image holds only `site/`, which is the public website, so the package can be
public and the host needs no registry login either. **Zero credentials touch the
VPS.**

The workflow refuses to publish if it finds a credential pattern anywhere under
`site/`, because a public image would otherwise publish it to the world.

## This VPS is shared, so the site does not take port 80

The VPS at `187.77.25.50` already runs **Ledgerium AI** and **Compassion
Benchmark**, and port 80 is owned by **Nginx Proxy Manager**, identified by name
in the 2026-08-18 deployment pass in `ops/NIGHTLY-LOG.md`.

The site therefore listens on **8973** and the existing proxy forwards to it.
Binding 80 directly would fight the proxy and could take a live product offline,
which is not a trade worth making to save one configuration step.

### Wiring the proxy

In Nginx Proxy Manager, add a host entry:

- domain: `6s-success.com` and `www.6s-success.com`
- forward to: `127.0.0.1` port `8973` (or the container name `6s-success` port
  `80` if Nginx Proxy Manager shares a Docker network with it)
- request a certificate for both names, now that DNS points here

As of the 2026-08-18 pass, port 80 still returned "Default Site" for the domain,
meaning no host entry for `6s-success.com` exists yet in Nginx Proxy Manager.
This is now the only remaining step. It needs the Nginx Proxy Manager panel,
which no session so far has had access to.

## Rolling back

Every build is also tagged with its short commit SHA. To roll back, change the
`image:` line in the compose to that tag and redeploy:

```yaml
image: ghcr.io/klingdom/6s-success:1a2b3c4
```

## What Phil needs to do

Three of the four original steps are done, per the 2026-08-18 deployment pass
recorded in `ops/NIGHTLY-LOG.md`:

- ~~Make the package public~~ done. The image pulls without a registry login.
- ~~Paste the compose~~ done, after fixing two silent faults: an unqualified
  image name that let Docker reuse a stale local image instead of pulling from
  `ghcr.io`, and a volumes entry that mounted a local nginx config over the
  one in the image. `ops/verify_deploy.py` passed 10 of 10 against the running
  container afterward.
- ~~Point the domain at the VPS~~ done. DNS moved to `187.77.25.50`.

**One step is left: the Nginx Proxy Manager host entry.**

`hpanel.hostinger.com/vps/1369835` has a Nginx Proxy Manager instance already
running, fronting Ledgerium AI on port 80. Add a proxy host there:

- domain: `6s-success.com` and `www.6s-success.com`
- forward to: `127.0.0.1` port `8973`
- request a certificate for both names

No session so far has had access to the Nginx Proxy Manager panel to do this.
Once it is done, `python ops/verify_deploy.py https://6s-success.com` should
pass against the real domain instead of a Host header override.

## Verifying it worked

The check is not "the container is green". A healthy container proves nginx
started, not that the site is correct. Run this from anywhere:

```bash
python ops/verify_deploy.py https://6s-success.com
```

It fetches every page, checks the ones that must exist, confirms the short URLs
printed in the book resolve, and confirms the site is not still the parking page.
