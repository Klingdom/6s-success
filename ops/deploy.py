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

# Written the moment this script confirms production live at a specific
# build id, and nowhere else. Found 2026-09-14: a session holding the VPS
# key deployed, confirmed production current by build id, then edited
# site/standards.html in the same pass, which moved the repo's own build id
# on again. Nothing recorded the confirmed-live moment anywhere durable, so
# a later session with no egress (every cloud sandbox) had no way to tell
# "never redeployed in weeks" apart from "one file behind since an hour
# ago", and ops/dashboard.py could only ever carry forward whatever
# deploy_last_verdict happened to be sitting in ops/state.json from before
# this deploy, which was still "stale". This file is the only place that
# can observe a real, credentialed deploy; write down what it saw.
VERDICT_PATH = os.path.join(ROOT, "ops", "deploy-verdict.json")


def classify_publish(runs, head_sha, ancestors):
    """Pure logic: what is the image build for this commit actually doing?

    `runs` is newest-first, each {"sha", "status", "conclusion"}.
    `ancestors` answers "does this run's commit contain head_sha", so the
    caller owns git and this stays testable without a repository.

    WHY THIS EXISTS
    ---------------
    When the live build id does not match the repository, deploy.py used to
    say, always: "Usually the image has not finished publishing: check `gh run
    list`, then run this again."

    That is right for the common case and wrong for the one that actually
    strands work. On 2026-09-30 a site change was pushed, its push-triggered
    build FAILED on a fault in a concurrent session's commit (a misordered
    NIGHTLY-LOG.md entry, nothing to do with the change), and the upstream fix
    for that fault touched no `site/**` path. publish-image.yml is correctly
    filtered to `site/**`, `Dockerfile` and itself, so it declined to rebuild,
    and the change sat with no image at all. Re-running deploy.py would have
    reported the same mismatch forever, and its own advice was to do exactly
    that.

    Four outcomes, because they need four different actions:

      building  wait, the advice deploy.py already gave
      ready     an image exists; a mismatch now is registry or pull lag
      failed    retrying deploy will NEVER help; fix the build or dispatch
      none      no run covers this commit at all; dispatch one

    "unknown" is separate and deliberate: no gh, no auth, no network. That is
    reported as unchecked rather than folded into "none", because "nobody
    built it" and "I could not look" are different facts and only one of them
    is a reason to act.
    """
    if runs is None:
        return "unknown", None
    for r in runs:
        if not ancestors(r.get("sha") or ""):
            continue
        status = (r.get("status") or "").lower()
        if status != "completed":
            return "building", r
        concl = (r.get("conclusion") or "").lower()
        if concl == "success":
            return "ready", r
        return "failed", r
    return "none", None


PUBLISH_ADVICE = {
    "building": ("an image build covering this commit is still running. "
                 "Wait for it, then run this again."),
    "ready":    ("an image build covering this commit already succeeded, so "
                 "the image exists. A mismatch now is registry or pull lag; "
                 "run this again shortly."),
    "failed":   ("THE IMAGE BUILD FOR THIS COMMIT FAILED, so no image "
                 "containing this change was ever published and running this "
                 "again will not change that. Read the run, fix what it "
                 "found, or dispatch a fresh build: "
                 "gh workflow run \"Publish site image\" --ref main"),
    "none":     ("NO IMAGE BUILD COVERS THIS COMMIT. publish-image.yml only "
                 "triggers on site/**, Dockerfile and itself, so a site "
                 "change whose build failed, or that landed behind one, can "
                 "sit with no image at all. Dispatch one: "
                 "gh workflow run \"Publish site image\" --ref main"),
    "unknown":  ("could not ask GitHub what the image build is doing (no gh, "
                 "no auth, or no network), so why production differs is "
                 "UNCHECKED. That is not the same as the image being on its "
                 "way."),
}

def _gh_runs(limit: int = 12):
    """Recent 'Publish site image' runs, newest first, or None if not asked.

    None means the question could not be put to GitHub, not that there are no
    runs. classify_publish() keeps those apart on purpose.
    """
    import json
    try:
        p = subprocess.run(
            ["gh", "run", "list", "--workflow", "Publish site image",
             "--limit", str(limit), "--json", "headSha,status,conclusion"],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
    except Exception:                                          # noqa: BLE001
        return None
    if p.returncode != 0:
        return None
    try:
        raw = json.loads(p.stdout or "[]")
    except Exception:                                          # noqa: BLE001
        return None
    return [{"sha": r.get("headSha") or "", "status": r.get("status") or "",
             "conclusion": r.get("conclusion") or ""} for r in raw]


def _head_sha():
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True, timeout=30)
        return p.stdout.strip() if p.returncode == 0 else ""
    except Exception:                                          # noqa: BLE001
        return ""


def _contains(head_sha):
    """Does a run's commit contain HEAD? Unknown objects answer no, safely."""
    def ancestors(run_sha):
        if not run_sha or not head_sha:
            return False
        try:
            p = subprocess.run(
                ["git", "merge-base", "--is-ancestor", head_sha, run_sha],
                cwd=ROOT, capture_output=True, text=True, timeout=30)
            return p.returncode == 0
        except Exception:                                      # noqa: BLE001
            return False
    return ancestors


def publish_state():
    """(state, run) for the image build covering HEAD. See classify_publish."""
    head = _head_sha()
    return classify_publish(_gh_runs(), head, _contains(head))


def write_verdict_marker(build_id: str) -> None:
    """Record a confirmed-live build id, for a later egress-less run to read.

    Deliberately minimal: just enough for ops/dashboard.py to tell whether
    the repo has moved on since production was last actually confirmed
    current, and when that confirmation happened. Never read by this file
    itself; a separate concern (deploy_freshness.check() already does its
    own live check when it can reach the network) kept separate on purpose.
    """
    import datetime
    import json
    payload = {
        "verdict": "current",
        "build_id": build_id,
        "checked_at": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(VERDICT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


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


def live_build_id():
    """The build id production is serving, or None if it could not be read."""
    try:
        req = urllib.request.Request(BASE + "/build-id.txt",
                                     headers={"User-Agent": "6s-deploy"})
        return urllib.request.urlopen(req, timeout=25).read().decode(
            "utf-8", "replace").strip() or None
    except Exception:                                           # noqa: BLE001
        return None


def repo_build_id():
    import io
    p = os.path.join(ROOT, "site", "build-id.txt")
    if not os.path.exists(p):
        return None
    return io.open(p, encoding="utf-8").read().strip() or None


def _stamp(html: str):
    """The fingerprint of the stylesheet the home page asks for.

    The product count cannot tell an old build from a new one: it was 159
    before a deploy and 159 after, so on 2026-09-03 this script reported a
    successful deploy of a build production had never received. Everything in
    that release was invisible on the live site and the verdict said it
    matched.

    The ?v= hash changes whenever the CSS changes, which is whenever anything
    about the site's appearance changes, so comparing it answers the actual
    question: is production serving THIS build. It is not a perfect content
    hash, and a release that touches no CSS will not move it, so this is
    reported alongside the product count rather than instead of it.
    """
    m = re.search(r'assets/css/site\.css\?v=([0-9a-f]+)', html)
    return m.group(1) if m else None


def live_stamp():
    try:
        req = urllib.request.Request(BASE + "/", headers={"User-Agent": "6s-deploy"})
        return _stamp(urllib.request.urlopen(req, timeout=25).read().decode(
            "utf-8", "replace"))
    except Exception:                                           # noqa: BLE001
        return None


def repo_stamp():
    import io
    return _stamp(io.open(os.path.join(ROOT, "site", "index.html"),
                          encoding="utf-8").read())


def compose_drift(user):
    """Compare the compose file production actually deploys from against the
    one in this repository, ignoring comments and blank lines.

    Added 2026-09-20 with the crawl-log volume, because that volume made the
    difference matter for the first time. The host file at
    /opt/6s-success/docker-compose.yml is what `docker compose up` reads, but
    the Hostinger Docker Manager panel keeps its OWN copy of the same YAML and
    writes it over the host file whenever somebody clicks Redeploy there. So a
    change made by SSH can be reverted by a click, months later, by someone who
    has no idea they did it. Until now the two copies were identical apart from
    comments (diffed the same day), and nothing ever checked that they stayed
    that way.

    This does not repair anything. It prints the difference, because a deploy
    tool that silently rewrites the production compose file is a worse problem
    than the drift it is fixing. GitHub is the source of truth; this makes it
    observable whether production still agrees.
    """
    import io

    def meaningful(text):
        return [l.rstrip() for l in text.splitlines()
                if l.strip() and not l.strip().startswith("#")]

    ok, remote = ssh(user, "cat /opt/6s-success/docker-compose.yml")
    if not ok:
        print("  UNCHECKED: could not read the production compose file, so "
              "whether it still matches this repository is unknown.")
        return
    local_fp = os.path.join(ROOT, "docker-compose.hostinger.yml")
    try:
        local = io.open(local_fp, encoding="utf-8").read()
    except OSError:
        print("  UNCHECKED: docker-compose.hostinger.yml is missing here.")
        return
    a, b = meaningful(local), meaningful(remote)
    if a == b:
        print("  compose: production matches docker-compose.hostinger.yml")
        return
    print("  COMPOSE DRIFT: production does NOT match this repository.")
    only_repo = [l for l in a if l not in b]
    only_prod = [l for l in b if l not in a]
    for l in only_repo[:12]:
        print("    in repo, not in production : %s" % l.strip())
    for l in only_prod[:12]:
        print("    in production, not in repo : %s" % l.strip())
    print("    Fix by copying the repo file to /opt/6s-success/"
          "docker-compose.yml AND pasting it into the Hostinger panel, or "
          "the next Redeploy click puts it back.")


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
        if not os.path.exists(KEY + ".pub"):
            print("  no public key at %s.pub either, so the install command "
                  "below cannot be printed. Generate the pair first: "
                  "ssh-keygen -t ed25519 -f %s -N ''" % (KEY, KEY))
            return 2
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
    # The product count alone cannot tell a no-op from a real release: it read
    # 159 before and after the 2026-09-14 deploy that moved production from
    # build 3c70a770 to 497533af, and the verdict said "already matched".
    # Record the build id too, so the verdict says what actually happened.
    before_id = live_build_id()

    # What the Redeploy button does. Find the compose project rather than
    # assuming its path, because guessing here restarts the wrong thing.
    ok, out = ssh(user, "docker compose ls --format json 2>/dev/null || "
                        "docker ps --format '{{.Names}}\t{{.Image}}'")
    if not ok:
        print("  could not inspect docker: %s" % out[:200])
        return 1
    print("  docker: %s" % out[:300])

    compose_drift(user)

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
    # The question is whether production MATCHES the repository, not whether
    # it changed. Asking "did it change" reported a correct deploy of an
    # already-current site as a failure, which trains everybody to ignore the
    # verdict. A no-op deploy of a matching site is a success.
    want = repo_product_count()
    if after != want:
        print("  VERDICT production serves %s products against %s here, so it "
              "is still behind." % (after, want))
        return 1

    # The count matching is necessary and not sufficient. Ask whether the bytes
    # are this build's bytes.
    #
    # build-id.txt is the authority, because it is a hash of EVERY deployed
    # file. The stylesheet fingerprint below is kept as a second opinion, but
    # it cannot answer this on its own: on 2026-09-04 a release of 1,717 new
    # links, a rebuilt deck and a corrected PDF touched no CSS, so the
    # stylesheet hash matched and this script called production current while
    # it served none of it.
    live_id, mine_id = live_build_id(), repo_build_id()
    print("  build id live        : %s" % (live_id or "unreadable"))
    print("  build id in repo     : %s" % (mine_id or "missing"))
    if mine_id and live_id and live_id != mine_id:
        print("  VERDICT production is serving a DIFFERENT build. Every "
              "deployed byte is covered by this hash, so this is not a "
              "sampling artefact.")
        state, run = publish_state()
        print("  image build for this commit: %s" % state)
        print("  %s" % PUBLISH_ADVICE[state])
        return 1
    if mine_id and live_id is None:
        print("  VERDICT unknown: production did not serve build-id.txt, so "
              "this build cannot be confirmed live. Unchecked is not deployed.")
        return 1

    live, mine = live_stamp(), repo_stamp()
    print("  stylesheet live      : %s" % live)
    print("  stylesheet in repo   : %s" % mine)
    if live is None or mine is None:
        print("  VERDICT unknown: could not read the build stamp from one "
              "side, so I cannot say whether this build is live. Unchecked is "
              "not deployed.")
        return 1
    if live != mine:
        print("  VERDICT production is serving a DIFFERENT build. The product "
              "count matches because it did not change, which is exactly how "
              "this check used to pass while shipping nothing.")
        state, run = publish_state()
        print("  image build for this commit: %s" % state)
        print("  %s" % PUBLISH_ADVICE[state])
        return 1
    if before == after and before_id == live_id:
        print("  VERDICT production already matched the repository and still "
              "does, by product count AND build stamp.")
    else:
        print("  VERDICT production changed (build %s -> %s) and now matches "
              "the repository." % (before_id or "unreadable", live_id))
    write_verdict_marker(live_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
