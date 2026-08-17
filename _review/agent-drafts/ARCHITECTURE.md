# 6S Success Technical Architecture

> Canonical description of how 6s-success.com is actually built and served: a static site, an nginx container, a reverse proxy, and nothing else. Records what exists, what deliberately does not, and what must change before the business can take money.

## 1. Purpose

`ARCHITECTURE.md` answers a question every agent asks before touching anything:

> What is this system, really?

The answer is smaller than the document set around it suggests. There is no application server, no database, no authentication, and no backend. There is a folder of HTML files copied into an nginx image.

That simplicity is an asset. Protect it, and do not let the operating documents imply capability the system does not have.

Read with:

- `CLAUDE.md`
- `SYSTEM-REGISTRY.md` for the inventory of what exists and where
- `DEPLOY.md` for the actual deploy commands
- `RUNBOOK.md` for safe operating procedure
- `SECURITY.md`
- `DISASTER-RECOVERY.md`
- `RELEASES.md`
- `RISKS.md`

If a referenced file does not exist yet, do not invent its contents.

---

# 2. Prime Architectural Rule

**Do not add a moving part until a customer outcome requires it.**

A static site has no runtime to exploit, no database to corrupt, no dependency to patch at 2am, and no state to lose. Every component added takes some of that away.

Before adding a runtime, a database, a framework, or a third party service, record the decision in `DECISIONS.md` with the customer outcome that required it.

---

# 3. What Exists Today

Verified 2026-08-17 by reading the repository.

| Layer | Reality |
|---|---|
| Content | 14 HTML pages in `site/`, hand authored, no build step |
| Styling | 2 stylesheets in `site/assets/css/` |
| Behavior | 3 JavaScript files in `site/assets/js/`, plus `tools.json` |
| Fonts | 22 self hosted woff2 files, 3 families: Inter, Fraunces, Newsreader |
| Images | 5 files in `site/assets/img/` |
| Downloads | 2 files in `site/downloads/`, a 1.1 MB HTML book and a 53 MB PDF |
| Web server | nginx 1.27 alpine, config at `site/nginx/default.conf` |
| Image | `6s-success:latest`, built from `Dockerfile` at the repository root |
| Container | `6s-success`, restart policy `unless-stopped` |
| TLS | Traefik v3.1 with Let's Encrypt, TLS ALPN challenge |
| Host | One Hostinger VPS |
| Domain | 6s-success.com, supplied to Traefik as `DOMAIN` from `.env` |

Total files under `site/`: 58.

---

# 4. The Request Path

```
browser
  -> DNS A record for 6s-success.com
  -> Hostinger VPS, ports 80 and 443
  -> Traefik (container: traefik)
       port 80 redirects to 443
       certificate resolver "le", Let's Encrypt, TLS ALPN challenge
       router rule Host(6s-success.com) or Host(www.6s-success.com)
  -> web container (6s-success), port 80 on the internal "web" network
  -> nginx
       try_files $uri $uri.html $uri/ =404
  -> a static file from /usr/share/nginx/html
```

Nothing in this path executes application code. Every response is a file on disk.

---

# 5. Two Deployment Topologies

The repository defines two, and they must not run at once because they share the container name and image.

## docker-compose.yml

Plain VPS. Publishes host port `8973` to container port 80. No TLS. Reachable at `http://SERVER_IP:8973`. Traefik labels are present but commented out.

Use for a bare host or a quick check.

## docker-compose.proxy.yml

The production shape. Brings up Traefik and the web container on a shared `web` network, claims ports 80 and 443, and obtains an auto renewing certificate. Requires `DOMAIN` and `ACME_EMAIL` in `.env`, and requires ports 80 and 443 to be free.

Use for the live domain.

**Which file is currently running on the VPS is UNKNOWN from this repository.** Running `docker compose ls` and `docker ps` on the host would establish it. Do not assume.

---

# 6. The Build

`Dockerfile`, at the repository root:

1. `FROM nginx:1.27-alpine`
2. copies `site/nginx/default.conf` to `/etc/nginx/conf.d/default.conf`
3. copies `site/` to `/usr/share/nginx/html`
4. removes `nginx` and `.gitignore` from the web root
5. exposes 80
6. declares a healthcheck: `wget -qO- http://localhost/` every 30s

The build context is the repository root, because Hostinger's Docker Manager clones the repository and builds from there. `.dockerignore` keeps the operating documents, agent definitions, super prompts, and working directories out of the context.

There is no compilation, bundling, transpiling, or minification step. What is in `site/` is what is served.

---

# 7. Client Side Behavior

`site/assets/js/site.js` provides navigation, reveal animations, a cart drawer, and the cart itself.

The cart is a `localStorage` key, `sixs_cart_v1`. It never leaves the browser. There is no cart server, no session, and no order record.

`site/cart.html` states that secure checkout arrives in v2. This is the architectural root of `RISK-0001`: the cart is complete and the path out of it does not exist.

`site/shop.html` is driven by `site/assets/js/data.js`, `shop.js`, and `tools.json`.

---

# 8. What Deliberately Does Not Exist

Recording absences matters as much as recording components, because agents otherwise assume they are there.

- no backend or application server
- no database of any kind
- no user accounts, login, session, or authentication
- no payment processing
- no server side form handling; all 14 form handlers are `onsubmit="return false"`
- no analytics, advertising pixels, session recording, or third party trackers, stated as a promise in `site/privacy.html`
- no external network requests from any page, including fonts, which are self hosted
- no CDN
- no CI, no `.github` directory, no workflows
- no staging environment

Several of these are deliberate and good. Several are `RISKS.md` entries. They are not the same list, and the difference matters:

| Absence | Deliberate? |
|---|---|
| Backend, database, accounts | Yes, and worth defending |
| External requests, CDN, trackers | Yes, a privacy and performance choice |
| Payment | No, RISK-0001 |
| Form handling and capture | No, RISK-0012 |
| Staging and CI | No, RISK-0007 and RISK-0010 |

---

# 9. State And Persistence

The only persistent volume in the production stack is `letsencrypt`, holding `acme.json`, the certificate store.

Everything else is derived:

- the image rebuilds from the repository
- the site content is in git
- the cart lives in the visitor's browser
- there is no customer data at rest anywhere in this system

This is why the site is unusually recoverable, and why `DISASTER-RECOVERY.md` has a far smaller problem to solve than its length implies. Losing the host loses uptime, not data.

The single dependency for rebuilding is read access to the repository, which is currently broken. See `RISK-0002`.

---

# 10. Repository Layout

| Path | Contains |
|---|---|
| `*.md` at root | The operating system: control documents |
| `claude/agents/` | 14 specialist agent definitions |
| `super prompts/` | 22 reusable generation prompts |
| `site/` | The published website, and only that |
| `ops/` | The measurement layer, see section 11 |
| `content/` | Product source: book, manual, decks, games, app, video, appendix |
| `business/ docs/ growth/ product/` | Working directories, currently empty |
| `Dockerfile`, `docker-compose*.yml`, `.env` | Infrastructure, deliberately at root |

The split of website from operating system happened on 2026-08-16. Before that the site was at the root. `DEPLOY.md` records the change.

`.env` is tracked in git on purpose. It holds `DOMAIN` and `ACME_EMAIL`, which are public facts. `.gitignore` names the files that genuine secrets belong in instead, and none of them are tracked.

---

# 11. The Measurement Layer

`ops/dashboard.py` reads the repository, the GitHub issue list, and the product folders on disk, then writes three artifacts:

- `EXECUTIVE-DASHBOARD-LIVE.md`, the at a glance read
- `ops/dashboard.html`, the same content styled
- `ops/state.json`, machine readable, for trend tracking

None of the three is hand maintained. Do not edit them. Re run the script.

This is the only executable code in the repository outside the website, and it is a genuine architectural component: it is how the system observes itself. `ops/build_resources.py` builds the resources page. `ops/nightly-routine.json` configures the nightly loop described in `LOOP.md`.

Note the coupling: `ops/dashboard.py` reads product state from an absolute Windows Desktop path. It therefore produces complete results only on the owner's machine. Elsewhere those counts will be wrong or zero. See `RISK-0011`.

---

# 12. Architectural Consequences

Each of these follows from the architecture rather than from any decision made in isolation.

**A static site cannot take money by itself.** Payment requires either a hosted checkout the site links out to, or a small server side component. The first preserves this architecture. The second does not. This is a decision, not a detail, and belongs in `DECISIONS.md`.

**A static site cannot capture a form.** The same choice applies: a hosted form endpoint, or a backend.

**A static site cannot personalize.** The product model in `PRODUCT-CATALOG.md` describes per household personalization across 114 micro zones. The current architecture cannot deliver it. The unshipped PWA prototype in `content/app-mvp/` is the intended answer, and shipping it would be the first real runtime this business has.

**A static site is very cheap and very safe.** Do not surrender that for a feature that has not been asked for by a paying customer.

---

# 13. Extension Points, In Order Of Cost

| Need | Lowest cost option that preserves the architecture |
|---|---|
| Take payment | Link to a hosted checkout or payment link per product |
| Capture email | A hosted form endpoint that posts from the static page |
| Measure demand | A privacy respecting analytics option, subject to `RISK-0005` |
| Personalize | The PWA, client side, no server |
| Sell decks or physical goods | A hosted store, or fulfillment by a third party |

Every row above avoids adding a runtime. Exhaust this table before proposing a backend.

---

# 14. Verification Commands

Read only. Run these before believing anything in this file.

```bash
# what the repository says
ls site/*.html | wc -l
grep -c 'onsubmit="return false"' site/*.html

# what the host says (on the VPS)
docker ps
docker compose ls
docker inspect 6s-success --format '{{.Config.Image}} {{.State.Health.Status}}'
docker image inspect 6s-success:latest --format '{{.Id}}'
docker volume ls
```

The image digest is the answer to "what is running". `RELEASES.md` governs how that digest ties back to a commit.

---

# 15. Known Unknowns

| Unknown | What would establish it |
|---|---|
| Which compose file is live | `docker compose ls` on the VPS |
| The running image digest | `docker image inspect` on the VPS |
| VPS specification and resource headroom | `nproc`, `free -h`, `df -h` on the host |
| Whether the healthcheck is passing | `docker inspect` health status |
| Certificate expiry and renewal history | Inspect the `letsencrypt` volume, or the served certificate |
| Whether DNS points where we think | Resolve the A record from outside |
| Actual page weight of the site | Measure served bytes for the heaviest page |

Do not fill these in from memory. Measure them, then record them in `SYSTEM-REGISTRY.md`.

---

# 16. Final Principle

The architecture is currently the least risky part of this business.

Fourteen static pages behind a reverse proxy will not fall over, will not leak customer data it does not hold, and can be rebuilt from a git clone.

The failure mode to guard against is not technical fragility. It is architectural ambition: adding a database, a framework, or a service because the operating documents describe a system larger than the one that exists.

Grow the architecture only when a paying customer needs something it cannot do.

Right now, exactly one thing qualifies: it cannot accept their money.
