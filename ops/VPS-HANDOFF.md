# Prompt for the Claude Code instance running on the VPS

Paste everything below the line into the Claude Code session at
<https://bos.hostingervps.com/2041/>.

It is written to be self contained: that instance has none of this session's
context, and it should not need any.

---

You are working directly on the 6S Success production VPS. A separate Claude Code
session runs on the owner's laptop and has been building the site; it cannot
reach this machine yet. Your job is to report what is here, open a door so the
laptop session can work directly, and get the website serving.

Do not guess at any of this. Run the commands and report what they actually say.

## Step 1. Report the facts

Run these and paste the full output back to the owner:

```bash
echo "PUBLIC IP:"; curl -s https://api.ipify.org; echo
echo "HOSTNAME:"; hostname
echo "OS:"; cat /etc/os-release | head -2
echo "DOCKER:"; docker --version; docker compose version
echo "RUNNING CONTAINERS:"; docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
echo "ALL CONTAINERS:"; docker ps -a --format '{{.Names}}\t{{.Status}}'
echo "PORTS IN USE:"; (ss -tlnp || netstat -tlnp) 2>/dev/null | grep LISTEN
echo "DISK:"; df -h / | tail -1
echo "COMPOSE PROJECTS:"; ls -la /root 2>/dev/null; find / -maxdepth 4 -name "docker-compose*.y*ml" -not -path "*/node_modules/*" 2>/dev/null | head
```

**The public IP is the single most important line.** The domain currently points
at Hostinger's parking page, and it cannot be repointed until that IP is known.

## Step 2. Let the laptop session in

Append this public key so the laptop can SSH here and deploy directly. It is a
public key: it grants nothing on its own and is safe to paste.

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL2nyJ4LvhNlLlGxWCIFkWalYhsMjGySG1Qfp9ahs7Gc claude-code@6s-success-vps" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys
grep -c "claude-code@6s-success-vps" ~/.ssh/authorized_keys
```

Then confirm SSH is actually reachable from outside:

```bash
grep -E "^(Port|PermitRootLogin|PubkeyAuthentication|PasswordAuthentication)" /etc/ssh/sshd_config
systemctl is-active ssh sshd 2>/dev/null
ufw status 2>/dev/null || iptables -L INPUT -n | head -20
```

If a firewall blocks 22, say so rather than opening it. That is the owner's call.

## Step 3. Deploy the site

The website is published as a container image, so **nothing needs to be cloned or
built here**. Check the image is reachable first:

```bash
docker pull ghcr.io/klingdom/6s-success:latest
```

If that fails with **denied** or **unauthorized**, stop and tell the owner: the
GitHub package is still private, and he must set it to public at
GitHub, repository Klingdom/6s-success, Packages, 6s-success, Package settings,
Change visibility. Do not work around this by adding a registry credential here.

Once the pull succeeds:

```bash
mkdir -p /opt/6s-success && cd /opt/6s-success
cat > docker-compose.yml <<'YAML'
services:
  web:
    image: ghcr.io/klingdom/6s-success:latest
    container_name: 6s-success
    restart: unless-stopped
    ports:
      - "80:80"
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
YAML
docker compose up -d
docker compose ps
```

If port 80 is already taken by something else, do not kill it. Change the
mapping to `"8973:80"`, report what was holding 80, and let the owner decide.

## Step 4. Prove it works, from outside

A running container proves nginx started. It does not prove the site is right.

```bash
curl -s -o /dev/null -w "home: %{http_code}\n" http://localhost/
curl -s -o /dev/null -w "404 path: %{http_code}  (MUST be 404, not 200)\n" http://localhost/does-not-exist-xyz
curl -s http://localhost/ | grep -o "<title>[^<]*</title>"
curl -s -o /dev/null -w "short url /resources: %{http_code}\n" http://localhost/resources
curl -s -o /dev/null -w "css: %{http_code}\n" http://localhost/assets/css/site.css
```

Expect: home 200, the nonsense path **404**, the title containing "6S Success",
/resources 200 without a .html suffix, css 200.

The 404 check matters more than it looks. Hostinger's parked domain answers 200
on every path, so a check that only looks for 200 will call a parked domain a
healthy website.

## Step 5. Report back

Give the owner, in plain words:

1. the public IP
2. whether the SSH key went in and whether port 22 is reachable
3. whether the image pulled, or that the package is still private
4. the five check results from step 4
5. anything you found that nobody asked about

## Rules

- Do not put any password, API key, or token into a file under a web root.
- Do not delete a container, volume, or image you did not create in this session.
- Do not change DNS, firewall rules, or anything billable. Report and let the
  owner decide.
- If something is irreversible or you are unsure, stop and ask.
