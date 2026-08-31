"""Prove gate_generator_ownership catches a hand edit to a generated file.

The gate exists for issue #26: nine occasions where a generator was one run
away from deleting content its own template does not produce. Until now it has
only ever been seen firing on drift it happened to stumble into, never on a
fault planted deliberately, and for five cycles it was not running at all.

Testing it is awkward because it refuses to run on a dirty tree, so the edit has
to be committed before it can be seen. Committing on the real branch to test a
check is not acceptable, so this uses a detached git worktree: a full second
checkout sharing the same object database, where a commit is free and throwing
the whole thing away afterwards costs nothing.

Two assertions, and the second matters as much as the first:

    a hand edit to a generated file is reported, naming that file;
    an untouched checkout is not reported.

Without the second, a gate that failed on everything would pass this test.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# site/resources.html is wholly rebuilt by ops/build_resources.py, which is in
# the gate's list and does not need the gitignored source photographs, so this
# works in a CI checkout as well as on the machine holding the images.
#
# The first version of this test used site/about.html and reported the gate as
# broken. It was not. about.html is a hand written page whose head blocks are
# wired in by generators; its body is nobody's output and survives a build
# untouched, which is exactly right. Verified before believing the failure, by
# planting a marker in three pages and running the generators over them:
# about.html kept it, resources.html and zones/index.html did not. Choosing a
# target for a test like this is a claim about ownership and has to be checked
# like one.
TARGET = os.path.join("site", "resources.html")
MARK = "<!-- planted by test_generator_ownership.py, must not survive a build -->"


def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                       text=True, timeout=300)
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr[:300]))
    return r.stdout


def preflight(cwd: str) -> str:
    r = subprocess.run([sys.executable, os.path.join("ops", "preflight.py"), "--own"],
                       cwd=cwd, capture_output=True, text=True, timeout=1800,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return (r.stdout or "") + (r.stderr or "")


def ownership_line(out: str) -> str:
    for line in out.splitlines():
        if "generator-ownership" in line and line.strip().startswith("FAIL"):
            return line.strip()
    return ""


def main() -> int:
    # This test runs preflight, and preflight runs this test. Left alone that
    # recurses without bound; it only stopped before because a worktree inside
    # a worktree failed to create. When preflight is the caller, say so and do
    # nothing, rather than relying on an accident to break the cycle.
    if os.environ.get("SIXS_UNDER_PREFLIGHT"):
        print("  skipped: preflight is the caller, and this test runs "
              "preflight. Run it directly to exercise the gate.")
        return 0

    if not shutil.which("git"):
        print("  no git here, cannot exercise the gate. NOT VERIFIED.")
        return 0

    tmp = tempfile.mkdtemp(prefix="6s-own-")
    wt = os.path.join(tmp, "wt")
    bad = []
    try:
        try:
            git("worktree", "add", "--detach", wt, "HEAD")
        except RuntimeError as e:
            print("  could not create a worktree (%s). NOT VERIFIED." % e)
            return 0

        # The catalogue is gitignored, so a fresh checkout does not have it and
        # several generators would produce different output without it.
        subprocess.run([sys.executable, os.path.join("ops", "build_catalog.py"),
                        "--build"], cwd=wt, capture_output=True, timeout=900)
        git("add", "-A", cwd=wt)
        git("-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "-m", "baseline", cwd=wt, check=False)

        # 1. An untouched checkout must not be reported. If this fires, the
        #    gate cannot distinguish anything and the next assertion is
        #    meaningless.
        line = ownership_line(preflight(wt))
        if line:
            bad.append("an untouched checkout was reported as drift: %s" % line[:200])

        # 2. A hand edit to a generated file must be reported, by name.
        page = os.path.join(wt, TARGET)
        src = io.open(page, encoding="utf-8").read()
        io.open(page, "w", encoding="utf-8", newline="").write(
            src.replace("</main>", MARK + "\n</main>", 1))
        git("-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "-am", "hand edit a generated page", cwd=wt)

        out = preflight(wt)
        line = ownership_line(out)
        if not line:
            bad.append("a hand edit to %s was NOT reported" % TARGET)
        elif "resources.html" not in line:
            bad.append("drift was reported but did not name the edited file: %s"
                       % line[:200])
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt],
                       cwd=ROOT, capture_output=True, timeout=300)
        shutil.rmtree(tmp, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                       capture_output=True, timeout=120)

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  a hand edit to a generated page is reported by name, "
              "and an untouched checkout is not")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
