"""Prove `preflight.py --skip-tests` alone now catches generator drift.

Found 2026-11-16: a real commit (the six-cleaning-product-types catalog fix)
regenerated six zone pages but never re-ran ops/build_resources.py, leaving
site/resources.html's room kit lists and product-type counts stale. That
exact defect is what gate_generator_ownership exists to catch
(test_generator_ownership.py already proves it can), and it DID catch it,
correctly, three times in a row in CI. It did not catch it locally, before
the commit landed, because the gate only ran under an explicit --own flag,
and no local pre-commit habit in this repository actually passes that flag:
every recent cycle's own log entries run `preflight.py --skip-tests`, which
used to reach gate_generator_ownership only through gate_tests (which
--skip-tests explicitly does not run). So the one check operators actually
run before every push was skipping the one gate that would have caught this.

Fixed by making `--skip-tests` also run gate_generator_ownership directly
(it is cheap on its own; the 90-minute cost --skip-tests exists to avoid is
gate_tests, a different gate). This test proves that specific wiring, the
same way test_generator_ownership.py proves the gate itself: a throwaway git
worktree, a hand edit to a page a generator owns, and two assertions.

    `preflight.py --skip-tests` (no --own) reports a hand edit to a
    generated page, naming it;
    an untouched checkout stays silent under the same flag.

It does not need test_generator_ownership.py's recursion guard for the
reason that test was built: --skip-tests never runs gate_tests, so it can
never call this file back. It needs the SAME guard for a different reason,
found live the first time this file ran inside gate_tests() rather than
standalone: gate_tests() bounds every test file at 700s (_run_bounded), and
this test's own inner preflight(wt) calls already budget up to 680s each,
twice, for a worktree build-catalogue step on top. On a quiet machine that
fits; under the real contention this sandbox's own nightly log documents
repeatedly (several concurrent operator sessions sharing one host), it does
not, and the test failed by name with subprocess.TimeoutExpired, not a real
regression. test_generator_ownership.py's own `--own` path(1800s inside its
nested call) would hit the identical wall if it ever ran that path under
gate_tests, which is exactly why it skips there instead: this test follows
the same convention, skipping under SIXS_UNDER_PREFLIGHT and relying on
being run directly (as this file's own fail-then-pass proof was) for real
verification, the same tradeoff gate_ops_test_suite_matches_gate_tests
already documents and guards for the sibling test.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Same target as test_generator_ownership.py, for the same reason: wholly
# rebuilt by ops/build_resources.py, which needs no gitignored source photos.
TARGET = os.path.join("site", "resources.html")
MARK = ("<!-- planted by test_generator_ownership_skip_tests.py, "
        "must not survive a build -->")


def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                       text=True, timeout=300)
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr[:300]))
    return r.stdout


def preflight(cwd: str) -> str:
    # 2026-11-16: this ran at timeout=680 and timed out in CI's checks.yml
    # run 3787, failing gate_tests on the whole repository over a single
    # test's own budget, not a real defect. --skip-tests still runs dozens
    # of other gates beyond gate_generator_ownership (affiliate reports,
    # network-dependent checks with their own multi-minute budgets, and
    # more), so "the generator chain itself is cheap" does not bound the
    # whole call the way the comment at its call site implies. This test
    # calls it twice, so a slow CI runner can exceed 680s on legitimate
    # work with no hang involved. Matched to test_generator_ownership.py's
    # own precedent (timeout=1800 for its single --own call) rather than
    # re-guessing a tighter number this repository has already proven wrong
    # once.
    r = subprocess.run(
        [sys.executable, os.path.join("ops", "preflight.py"), "--skip-tests"],
        cwd=cwd, capture_output=True, text=True, timeout=1800,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return (r.stdout or "") + (r.stderr or "")


def ownership_line(out: str) -> str:
    for line in out.splitlines():
        if "generator-ownership" in line and line.strip().startswith("FAIL"):
            return line.strip()
    return ""


def main() -> int:
    # See the module docstring: this is a time-budget guard, not a
    # recursion guard (--skip-tests cannot call gate_tests back). Run
    # directly to exercise the gate for real.
    if os.environ.get("SIXS_UNDER_PREFLIGHT"):
        print("  skipped: preflight is the caller, and this test's own "
              "nested preflight calls do not fit gate_tests()'s 700s "
              "per-file bound under real contention. Run it directly to "
              "exercise the gate.")
        return 0

    if not shutil.which("git"):
        print("  no git here, cannot exercise the gate. NOT VERIFIED.")
        return 0

    tmp = tempfile.mkdtemp(prefix="6s-own-skip-")
    wt = os.path.join(tmp, "wt")
    bad = []
    try:
        try:
            git("worktree", "add", "--detach", wt, "HEAD")
        except RuntimeError as e:
            print("  could not create a worktree (%s). NOT VERIFIED." % e)
            return 0

        subprocess.run([sys.executable, os.path.join("ops", "build_catalog.py"),
                        "--build"], cwd=wt, capture_output=True, timeout=900)
        git("add", "-A", cwd=wt)
        git("-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "--no-verify", "-m", "baseline", cwd=wt,
            check=False)

        # 1. An untouched checkout, checked under --skip-tests (no --own),
        #    must not be reported.
        line = ownership_line(preflight(wt))
        if line:
            bad.append("an untouched checkout was reported as drift under "
                       "--skip-tests: %s" % line[:200])

        # 2. A hand edit to a generated file, checked the same way, must be
        #    reported, by name, WITHOUT passing --own.
        page = os.path.join(wt, TARGET)
        src = io.open(page, encoding="utf-8").read()
        io.open(page, "w", encoding="utf-8", newline="").write(
            src.replace("</main>", MARK + "\n</main>", 1))
        git("-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "--no-verify", "-am", "hand edit a generated page",
            cwd=wt)

        out = preflight(wt)
        line = ownership_line(out)
        if not line:
            bad.append("a hand edit to %s was NOT reported under "
                       "--skip-tests alone" % TARGET)
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
        print("  ok  `preflight.py --skip-tests` alone (no --own) reports a "
              "hand edit to a generated page by name, and stays silent on "
              "an untouched checkout")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
