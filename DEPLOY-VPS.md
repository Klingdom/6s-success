# Deploying 6S Success to the Hostinger VPS

Everything here is set up. What remains is three clicks in two web panels, listed
at the bottom.

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

## Rolling back

Every build is also tagged with its short commit SHA. To roll back, change the
`image:` line in the compose to that tag and redeploy:

```yaml
image: ghcr.io/klingdom/6s-success:1a2b3c4
```

## What Phil needs to do

**1. Make the package public** (one time, after the first Action run)
GitHub, this repository, Packages, `6s-success`, Package settings, Change
visibility to Public. Without this the VPS gets a 403 on pull and would need a
registry login, which reintroduces a credential for no benefit.

**2. Paste the compose**
`hpanel.hostinger.com/vps/1369835/docker-manager/compose/6s-success/edit`
Replace the contents with `docker-compose.hostinger.yml` from this repository,
then Deploy.

**3. Point the domain at the VPS**
The A record for `6s-success.com` and `www` currently resolve to `2.57.91.91`,
which is Hostinger's **parked domain** page, and the nameservers are
`dns-parking.com`. Change the A records to this VPS's IP address. Until this is
done the site is running but nobody reaches it.

## Verifying it worked

The check is not "the container is green". A healthy container proves nginx
started, not that the site is correct. Run this from anywhere:

```bash
python ops/verify_deploy.py https://6s-success.com
```

It fetches every page, checks the ones that must exist, confirms the short URLs
printed in the book resolve, and confirms the site is not still the parking page.
