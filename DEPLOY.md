# Deploying the 6S Success website

The site is plain static files. This folder ships with everything needed to run it
as an nginx container: `Dockerfile`, `nginx/default.conf`, and `docker-compose.yml`.

---

## 1. Put it on GitHub

From this folder (`6S-Website`):

```bash
git init
git add .
git commit -m "6S Success website v1"
git branch -M main
# create an EMPTY repo on github.com first (no README), then:
git remote add origin https://github.com/<you>/6s-success.git
git push -u origin main
```

Note: the book PDF in `downloads/` is ~51 MB. GitHub allows it (hard limit is 100 MB
per file) but warns over 50 MB. If you prefer, either:
- leave it (works fine, just a warning), or
- track big binaries with Git LFS: `git lfs install && git lfs track "*.pdf" "*.png"`, or
- remove `downloads/` from git and upload those two files to the server separately.

---

## 2. Run it on the VPS via your Docker manager

The container serves the site on **port 80** inside Docker. You expose it either by
mapping a host port, or (better) by routing a domain to it through your reverse proxy.

### Option A0 — Hostinger Docker Manager (Ubuntu 24.04 + Docker)  ← this VPS
Hostinger's Docker Manager is a GUI over `docker compose`. Deploy this repo with it:
1. Push this folder to a **public** GitHub repo (private needs a deploy token).
2. hPanel → VPS → your server → **Docker Manager** → **Create / Deploy project**.
3. Choose **Docker Compose**, source = **Git repository**, paste the repo URL
   (`https://github.com/<you>/6s-success`). It reads `docker-compose.yml` at the root.
   Name the project `6s-success`.
4. Deploy. It clones the repo and runs `docker compose up -d`, which BUILDS the nginx
   image from the `Dockerfile` and starts the container as `8973:80`.
5. Open port **8973** (hPanel VPS firewall, and `ufw allow 8973/tcp` if ufw is on).
   Visit `http://<VPS_IP>:8973`.
6. Manage logs / restart / redeploy from the project's page. After a `git push`, hit
   **Redeploy** (or SSH: `cd 6s-success && git pull && docker compose up -d --build`).
Guaranteed fallback (you have full SSH + Docker): `git clone … && cd 6s-success && docker compose up -d --build`.

### Option A — build straight from the Git repo (Coolify, Dokploy, CapRover, Portainer "Git" stack)
1. New project / application / stack → source = **Git repository** → your repo URL, branch `main`.
2. Build method = **Dockerfile** (it is at the repo root).
3. Set the domain (these managers provision HTTPS via Let's Encrypt automatically), or
   map a host port like `8973:80` if you have no proxy.
4. Deploy. Re-deploy on each `git push` (enable the auto-deploy webhook if offered).

### Option B — Portainer / Dockge "Compose" stack
1. New Stack → paste the contents of `docker-compose.yml` (or point it at the repo).
2. Deploy. Reach it at `http://SERVER_IP:8973`.
3. To use a domain with HTTPS, delete the `ports:` block and add your proxy's
   labels/network (Traefik labels are pre-written and commented in the compose file;
   for Nginx Proxy Manager, add a Proxy Host pointing to `6s-success:80`).

### Option C — plain SSH (no manager UI)
```bash
git clone https://github.com/<you>/6s-success.git
cd 6s-success
docker compose up -d --build
```

### Updating
`git push` locally, then in the manager hit **Redeploy / Pull & recreate** (or on the
box: `git pull && docker compose up -d --build`).
