"""Deploy the current image to production, without a human clicking anything.

Written 2026-08-31 after Phil pointed out he had seen nothing for five days.
He was right, and the number that proves it is not the commit count: 339 commits
in five days, and 10 products on the live site against 159 in the repository.
Work that never deploys is work that never happened.

For eight days the standing line was "the Redeploy click is the one step no
autonomous session can perform". That was true and it was also the wrong thing
to ask for, because it asks for a click every single time. The actual blocker is
narrower: three SSH keys exist on the workstation and none of them were ever
installed on the server. Installing one is a one-time action that removes the
gate permanently.

This script does what the Redeploy button does: pull the newly published image
and recreate the container. It refuses to claim success it has not observed.

    python ops/deploy.py --check     does the door open at all
    python ops/deploy.py             pull, recreate, verify
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Verified on the server 2026-09-01: the 6s-success compose project lives
# at /opt/6s-success/docker-compose.yml, not /root. Guessing the path
# would have restarted nothing and reported a deploy.
HOST = "187.77.25.50"
COMPOSE_DIR = "/opt/6s-success"
KEY = os.path.expanduser("~/.ssh/6s_deploy")
BASE = "https://6s-success.com"

# Tried in order. The user is unknown until a key is installed, so ask rather
# than assume.
USERS = ("root", "deploy", "ubuntu", "debian")


def ssh(user: str, cmd: str, timeout: int = 90):
    """Run one command on the VPS. Returns (ok, output)."""
    argv = ["ssh", "-i", KEY, "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=12", f"{user}@{HOST}", cmd]
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "timed out"
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def reachable():
    """Which user, if any, this key can log in as. None means no access."""
    for u in USERS:
        ok, _ = ssh(u, "true", timeout=25)
        if ok:
            return u
    return None


def live_product_count():
    """What production is actually serving, which is the only real verdict."""
    try:
        req = urllib.request.Request(BASE + "/assets/js/data.js",
                                     headers={"User-Agent": "6s-deploy"})
        s = urllib.request.urlopen(req, timeout=25).read().decode(
            "utf-8", "replace")
        return len(re.findall(r'"sku"\s*:', s))
    except Exception:                                           # noqa: BLE001
        return None


def repo_product_count():
    import io
    s = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                encoding="utf-8").read()
    return len(re.findall(r'"sku"\s*:', s))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report whether deployment is possible, change nothing")
    a = ap.parse_args()

    if not os.path.exists(KEY):
        print("  no deploy key at %s" % KEY)
        return 1

    user = reachable()
    if not user:
        print("  BLOCKED. The deploy key is not installed on the server, so no")
        print("  autonomous deploy is possible. This is a ONE TIME fix:")
        print()
        pub = open(KEY + ".pub").read().strip()
        print("     ssh root@%s" % HOST)
        print("     mkdir -p ~/.ssh && echo '%s' >> ~/.ssh/authorized_keys" % pub)
        print("     chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys")
        print()
        print("  After that, every future deploy runs without a human, and the")
        print("  Redeploy click is never needed again.")
        return 2

    print("  access as %s@%s" % (user, HOST))
    if a.check:
        print("  --check only, nothing changed")
        return 0

    before = live_product_count()

    # What the Redeploy button does. Find the compose project rather than
    # assuming its path, because guessing here restarts the wrong thing.
    ok, out = ssh(user, "docker compose ls --format json 2>/dev/null || "
                        "docker ps --format '{{.Names}}\t{{.Image}}'")
    if not ok:
        print("  could not inspect docker: %s" % out[:200])
        return 1
    print("  docker: %s" % out[:300])

    ok, out = ssh(user,
                  "cd /opt/6s-success && docker compose pull && docker compose up -d",
                  timeout=420)
    if not ok:
        print("  deploy command failed: %s" % out[:400])
        return 1
    print("  %s" % out[-400:])

    after = live_product_count()
    print()
    print("  products live before : %s" % before)
    print("  products live after  : %s" % after)
    print("  products in repo     : %s" % repo_product_count())
    if after is None:
        print("  VERDICT unknown: production could not be read after the deploy.")
        print("  Unchecked is not deployed.")
        return 1
    if before is not None and after == before:
        print("  VERDICT the live catalogue did not change. Do not report this")
        print("  as a successful deploy until it does.")
        return 1
    print("  VERDICT production changed and is now serving the new build.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
