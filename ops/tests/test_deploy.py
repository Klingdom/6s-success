#!/usr/bin/env python3
"""
Prove deploy.py's own verdict logic says the right thing, without a real SSH
key or network access to the VPS.

No sandbox this project runs in has ever held ~/.ssh/6s_deploy (confirmed
2026-09-07: the file does not exist here), so every real invocation of
deploy.py in this history has taken the "no deploy key" early exit at line
one of main(). That means the actual verdict branching after a deploy
(product count, build id, stylesheet stamp, before/after) has never executed
anywhere this operator can see, the same blind spot test_check_live_links.py
and test_deploy_freshness.py already exist to close for their own files.
This monkeypatches reachable/ssh/live_*/repo_* so main()'s decision logic
runs directly.

Run:  python ops/tests/test_deploy.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import deploy as D                                             # noqa: E402


def run(argv, key_exists=True, pub_exists=True, reachable_user="root",
        docker_ok=True, deploy_ok=True, before=159, after=159, want=159,
        live_id="abc123", mine_id="abc123", live_stamp="css1",
        mine_stamp="css1"):
    """Run main() with every I/O boundary stubbed. Returns (exit_code, out).

    Uses real temp files for the key/pub check rather than monkeypatching
    os.path.exists, so the interpreter's own use of that function elsewhere
    during the run is never touched.
    """
    real = (D.KEY, D.reachable, D.ssh, D.live_product_count,
            D.repo_product_count, D.live_build_id, D.repo_build_id,
            D.live_stamp, D.repo_stamp, D.VERDICT_PATH, sys.argv)

    tmpdir = tempfile.mkdtemp()
    fake_key = os.path.join(tmpdir, "key")
    D.VERDICT_PATH = os.path.join(tmpdir, "deploy-verdict.json")
    if key_exists:
        open(fake_key, "w").write("fake private key")
        if pub_exists:
            open(fake_key + ".pub", "w").write("ssh-ed25519 AAAAfake test")

    def fake_ssh(user, cmd, timeout=90):
        if "docker compose ls" in cmd or "docker ps" in cmd:
            return docker_ok, "fake docker state" if docker_ok else "ssh refused"
        if "compose pull" in cmd:
            return deploy_ok, "pulled+up" if deploy_ok else "pull failed"
        return True, ""

    try:
        D.KEY = fake_key if key_exists else os.path.join(tmpdir, "missing")
        D.reachable = lambda: reachable_user
        D.ssh = fake_ssh
        seq = iter([before, after])
        D.live_product_count = lambda: next(seq)
        D.repo_product_count = lambda: want
        D.live_build_id = lambda: live_id
        D.repo_build_id = lambda: mine_id
        D.live_stamp = lambda: live_stamp
        D.repo_stamp = lambda: mine_stamp
        sys.argv = ["deploy.py"] + argv
        code = D.main()
        marker_path = os.path.join(tmpdir, "deploy-verdict.json")
        marker = None
        if os.path.exists(marker_path):
            with open(marker_path, encoding="utf-8") as f:
                marker = json.load(f)
        return code, marker
    finally:
        (D.KEY, D.reachable, D.ssh, D.live_product_count,
         D.repo_product_count, D.live_build_id, D.repo_build_id,
         D.live_stamp, D.repo_stamp, D.VERDICT_PATH, sys.argv) = real
        for p in (fake_key, fake_key + ".pub",
                  os.path.join(tmpdir, "deploy-verdict.json")):
            if os.path.exists(p):
                os.remove(p)
        os.rmdir(tmpdir)


def main() -> int:
    fails = []

    r, _ = run([], key_exists=False)
    if r != 1:
        fails.append(f"no deploy key must return 1 (blocked), got {r}")

    r, _ = run([], reachable_user=None)
    if r != 2:
        fails.append(f"key present but not installed on the server must "
                      f"return 2, got {r}")

    r, _ = run([], reachable_user=None, pub_exists=False)
    if r != 2:
        fails.append(f"key present, not installed, AND no .pub file must "
                      f"still return 2 with a clear message rather than "
                      f"crash (this is the real bug this file found: an "
                      f"unhandled FileNotFoundError), got {r}")

    r, m = run(["--check"])
    if r != 0:
        fails.append(f"--check with a reachable user must return 0, got {r}")
    if m is not None:
        fails.append(f"--check must change nothing, including the deploy "
                      f"verdict marker; got {m!r}")

    r, m = run([], docker_ok=False)
    if r != 1:
        fails.append(f"a failed docker inspect must return 1, got {r}")
    if m is not None:
        fails.append(f"a failed deploy must not write a 'current' marker; "
                      f"got {m!r}")

    r, _ = run([], deploy_ok=False)
    if r != 1:
        fails.append(f"a failed compose pull/up must return 1, got {r}")

    r, _ = run([], after=None)
    if r != 1:
        fails.append(f"unreadable product count after deploy must return 1 "
                      f"(unchecked is not deployed), got {r}")

    r, _ = run([], after=140, want=159)
    if r != 1:
        fails.append(f"a product count behind the repository must return 1, "
                      f"got {r}")

    r, m = run([], live_id="old999", mine_id="new123")
    if r != 1:
        fails.append(f"a build id mismatch must return 1 (different build "
                      f"live), got {r}")
    if m is not None:
        fails.append(f"a build id mismatch must not write a 'current' "
                      f"marker; got {m!r}")

    r, _ = run([], live_id=None, mine_id="new123")
    if r != 1:
        fails.append(f"an unreadable live build id when the repo has one "
                      f"must return 1 (unchecked is not deployed), got {r}")

    r, _ = run([], live_stamp=None)
    if r != 1:
        fails.append(f"an unreadable stylesheet stamp must return 1, got {r}")

    r, _ = run([], live_stamp="css-old", mine_stamp="css-new")
    if r != 1:
        fails.append(f"a stylesheet stamp mismatch must return 1 (this is "
                      f"the exact 2026-09-04 near-miss: matching product "
                      f"count, different build), got {r}")

    r, m = run([], before=159, after=159, want=159, live_id="build1",
               mine_id="build1")
    if r != 0:
        fails.append(f"an already-current site (before == after, everything "
                      f"matches) must return 0, got {r}")
    if not m or m.get("verdict") != "current" or m.get("build_id") != "build1":
        fails.append(f"a confirmed-current deploy must persist a marker "
                      f"naming the live build id, so a later egress-less "
                      f"run can tell a real confirmation from a stale carry "
                      f"(2026-09-14: this never happened, and a session's "
                      f"own confirmed deploy was invisible to the next run "
                      f"that could not itself reach the site); got {m!r}")
    if not m or "checked_at" not in m:
        fails.append(f"the marker must carry when it was confirmed, got {m!r}")

    r, m = run([], before=140, after=159, want=159, live_id="build2",
               mine_id="build2")
    if r != 0:
        fails.append(f"a real deploy that changed the count and now matches "
                      f"must return 0, got {r}")
    if not m or m.get("build_id") != "build2":
        fails.append(f"a real deploy (count changed) must also persist the "
                      f"marker with the new live build id; got {m!r}")

    for f in fails:
        print(f"  FAIL  {f}")
    total = 20
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
