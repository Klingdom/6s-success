#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_stray_probe_files() both fails loudly on a
leftover probe/fixture file and actually deletes it, and that it runs first
in main()'s own gate order, ahead of gate_existing and gate_tests.

Found 2026-09-10, this operator: a preflight run killed mid-audit (SIGTERM,
outer timeout) left site/zones/_visual_probe.html sitting on disk. The very
next preflight run hit gate_existing (audit_pages.py's "pages" gate) and
gate_tests (test_gate_zone_short_answer.py) BEFORE it ever reached
gate_no_stray_probe_files, which sat much later in main()'s own list. Both
misread the stray file as a real, malformed zone page and failed on that
symptom, naming nothing about the real cause; only cleaned up somewhere
between then and a third rerun, and this file's own docstring already
described exactly this shape of bug for two other cases (2026-09-03,
2026-09-05) without anyone noticing the gate itself still ran too late to
protect the gates ahead of it. Fixed by moving the run_gate() call to the
top of main(), right after bootstrap_fresh_sandbox(), and having the gate
delete what it finds after reporting it, so gate_existing/gate_tests in the
same run see a clean tree instead of inheriting the same failure twice
under two different, more confusing names.

Run:  python ops/tests/test_gate_no_stray_probe_files.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run_with_stray(name):
    tmp = tempfile.mkdtemp()
    zones = os.path.join(tmp, "zones")
    os.makedirs(zones)
    path = None
    if name is not None:
        path = os.path.join(zones, name)
        io.open(path, "w", encoding="utf-8").write("<html></html>")
    old_site, old_root = preflight.SITE, preflight.ROOT
    preflight.SITE = tmp
    preflight.ROOT = tmp
    os.makedirs(os.path.join(tmp, "ops", "tests"))
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_stray_probe_files()
        still_there = path is not None and os.path.exists(path)
        return list(preflight.FAIL), still_there
    finally:
        preflight.SITE, preflight.ROOT = old_site, old_root


def _run_with_tests_stray(name, is_dir=False):
    """Same shape, one level up: a stray under ops/tests/ instead of site/."""
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "zones"))
    tests_dir = os.path.join(tmp, "ops", "tests")
    os.makedirs(tests_dir)
    path = os.path.join(tests_dir, name)
    if is_dir:
        os.makedirs(path)
        io.open(os.path.join(path, "clean.pdf"), "wb").write(b"fake")
    else:
        io.open(path, "wb").write(b"fake")
    old_site, old_root = preflight.SITE, preflight.ROOT
    preflight.SITE = os.path.join(tmp, "site")
    os.makedirs(preflight.SITE)
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_stray_probe_files()
        still_there = os.path.exists(path)
        return list(preflight.FAIL), still_there
    finally:
        preflight.SITE, preflight.ROOT = old_site, old_root


def test_clean_tree_passes():
    fails, _ = _run_with_stray(None)
    assert fails == [], f"expected no failure on a clean tree, got {fails}"


def test_stray_visual_probe_fails_and_is_deleted():
    fails, still_there = _run_with_stray("_visual_probe.html")
    assert len(fails) == 1 and fails[0][0] == "stray-probe-files", fails
    assert "_visual_probe.html" in fails[0][1], fails[0][1]
    assert not still_there, "gate must delete the stray file it just reported"


def test_stray_fixture_file_also_caught():
    fails, still_there = _run_with_stray("_audit_catalog_fixture.html")
    assert len(fails) == 1 and fails[0][0] == "stray-probe-files", fails
    assert not still_there


def test_audit_catalog_fixture_with_live_pid_is_not_stray():
    """Found live 2026-10-01: two independent scheduled sessions sharing one
    sandbox collided when this gate ran while a SEPARATE, un-killed
    test_audit_catalog.py process (not this one) had its own
    _audit_catalog_fixture_<pid>.html genuinely open. The pid in the name
    exists so concurrent runs cannot share a path; this gate must read it
    back and leave a live writer's fixture alone rather than reporting and
    deleting it out from under the still-running process."""
    fails, still_there = _run_with_stray(
        "_audit_catalog_fixture_%d.html" % os.getpid())
    assert fails == [], (
        f"a fixture whose writer pid is still alive must not be reported, "
        f"got {fails}")
    assert still_there, (
        "a live writer's fixture must never be deleted out from under it")


def test_audit_catalog_fixture_with_dead_pid_still_caught():
    """The other half: a fixture naming a pid that is genuinely gone (the
    original killed-run shape this gate exists for) must still be caught
    and deleted, proving the live-pid exemption above did not accidentally
    exempt every pid-suffixed fixture. Same Popen-then-wait idiom
    test_audit_catalog.py's own dead-pid case uses, not os.fork (not
    available on Windows, and this repository's own pid-liveness helper is
    written to work there too)."""
    import subprocess
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    dead = p.pid
    try:
        os.kill(dead, 0)
        print("  pid %d still reads alive, so a dead-pid fixture could not "
              "be staged here. NOT VERIFIED." % dead)
        return
    except ProcessLookupError:
        pass
    except OSError:
        print("  pid %d liveness could not be determined here. "
              "NOT VERIFIED." % dead)
        return
    fails, still_there = _run_with_stray(
        "_audit_catalog_fixture_%d.html" % dead)
    assert len(fails) == 1 and fails[0][0] == "stray-probe-files", fails
    assert not still_there, "a dead writer's fixture must still be deleted"


def test_stray_ops_tests_file_caught_and_deleted():
    """A killed test_render_cards.py-shaped run, a file directly."""
    fails, still_there = _run_with_tests_stray("_scratch_render_cards.png")
    assert len(fails) == 1 and fails[0][0] == "stray-probe-files", fails
    assert "_scratch_render_cards.png" in fails[0][1], fails[0][1]
    assert not still_there


def test_stray_ops_tests_dir_caught_and_deleted():
    """The real regression: a killed test_gate_sample_pdf_spelling.py-shaped
    run leaving a whole DIRECTORY, not a bare file, under ops/tests/. The
    old os.remove()-only cleanup would raise IsADirectoryError, get
    silently swallowed by the bare except OSError, and leave the directory
    in place to fail every future run; this proves shutil.rmtree actually
    clears it."""
    fails, still_there = _run_with_tests_stray(
        "_tmp_sample_pdf_spelling", is_dir=True)
    assert len(fails) == 1 and fails[0][0] == "stray-probe-files", fails
    assert "_tmp_sample_pdf_spelling" in fails[0][1], fails[0][1]
    assert not still_there, "a stray directory must be rmtree'd, not left behind"


def test_pycache_under_ops_tests_is_not_a_stray():
    """Found 2026-09-26 in CI: the widened `ops/tests/_*` glob also matches
    `ops/tests/__pycache__`, Python's ordinary bytecode cache (created when
    CI's own test-collection step imports test modules rather than
    invoking them as scripts). That is normal operation, not a killed-run
    leftover, and the gate failed on it every single run, breaking CI
    permanently the moment the widening merged. A real __pycache__/ with a
    real .pyc inside must never be reported or deleted."""
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "zones"))
    tests_dir = os.path.join(tmp, "ops", "tests")
    pycache = os.path.join(tests_dir, "__pycache__")
    os.makedirs(pycache)
    io.open(os.path.join(pycache, "test_foo.cpython-311.pyc"),
            "wb").write(b"fake bytecode")
    old_site, old_root = preflight.SITE, preflight.ROOT
    preflight.SITE = os.path.join(tmp, "site")
    os.makedirs(preflight.SITE)
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_stray_probe_files()
        assert preflight.FAIL == [], (
            f"__pycache__ must never be reported as a stray probe file, "
            f"got {preflight.FAIL}")
        assert os.path.isdir(pycache), (
            "__pycache__ must never be deleted by this gate")
    finally:
        preflight.SITE, preflight.ROOT = old_site, old_root


def test_tracked_underscore_file_is_never_reported_or_deleted():
    """Found live 2026-09-29: ops/tests/_worktree.py, a real, checked-in
    helper module five gate-cleanliness tests import, matches this same
    `ops/tests/_*` glob. A tracked file can never be a killed-run leftover
    (a leftover is untracked by definition), so this gate must exempt
    anything git actually tracks, checked directly rather than by a second
    hand-maintained name list. Uses a real git repo, not a bare directory,
    to exercise the actual `git ls-files` call this exemption depends on."""
    import subprocess
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "site"))
    tests_dir = os.path.join(tmp, "ops", "tests")
    os.makedirs(tests_dir)
    tracked_path = os.path.join(tests_dir, "_worktree.py")
    io.open(tracked_path, "w", encoding="utf-8").write("# real helper\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp, capture_output=True)
    subprocess.run(["git", "-c", "user.email=t@example.com",
                    "-c", "user.name=t", "add", "-A"], cwd=tmp,
                   capture_output=True)
    subprocess.run(["git", "-c", "user.email=t@example.com",
                    "-c", "user.name=t", "commit", "-q", "-m", "initial"],
                   cwd=tmp, capture_output=True)
    old_site, old_root = preflight.SITE, preflight.ROOT
    preflight.SITE = os.path.join(tmp, "site")
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_stray_probe_files()
        assert preflight.FAIL == [], (
            f"a tracked file must never be reported as a stray probe "
            f"file, got {preflight.FAIL}")
        assert os.path.exists(tracked_path), (
            "a tracked file must never be deleted by this gate")
    finally:
        preflight.SITE, preflight.ROOT = old_site, old_root


def test_untracked_underscore_file_still_caught_in_a_real_repo():
    """The other half of the same fix: an actually untracked stray file,
    in a real git repo (not just a bare directory), must still be caught
    and deleted. Proves the tracked-file exemption above did not
    accidentally exempt everything."""
    import subprocess
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "site"))
    tests_dir = os.path.join(tmp, "ops", "tests")
    os.makedirs(tests_dir)
    subprocess.run(["git", "init", "-q"], cwd=tmp, capture_output=True)
    stray_path = os.path.join(tests_dir, "_scratch_leftover.html")
    io.open(stray_path, "w", encoding="utf-8").write("<html></html>")
    old_site, old_root = preflight.SITE, preflight.ROOT
    preflight.SITE = os.path.join(tmp, "site")
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_stray_probe_files()
        assert len(preflight.FAIL) == 1, preflight.FAIL
        assert "_scratch_leftover.html" in preflight.FAIL[0][1]
        assert not os.path.exists(stray_path), (
            "an untracked stray file must still be deleted")
    finally:
        preflight.SITE, preflight.ROOT = old_site, old_root


def test_clean_ops_tests_dir_passes():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "site"))
    os.makedirs(os.path.join(tmp, "ops", "tests"))
    old_site, old_root = preflight.SITE, preflight.ROOT
    preflight.SITE = os.path.join(tmp, "site")
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_stray_probe_files()
        assert preflight.FAIL == [], (
            f"expected no failure on a clean ops/tests/ tree, got {preflight.FAIL}")
    finally:
        preflight.SITE, preflight.ROOT = old_site, old_root


def test_runs_before_gate_existing_and_gate_tests_in_main():
    src = io.open(os.path.join(ROOT, "ops", "preflight.py"),
                  encoding="utf-8").read()
    start = src.index("\ndef main(")
    body = src[start:]
    probe_pos = body.index("run_gate(gate_no_stray_probe_files)")
    existing_pos = body.index("run_gate(gate_existing")
    tests_pos = body.index("run_gate(gate_tests)")
    assert probe_pos < existing_pos, (
        "gate_no_stray_probe_files must run before gate_existing, or a "
        "stray file from an earlier killed run pollutes the pages gate "
        "again before this gate ever gets to clear it")
    assert probe_pos < tests_pos, (
        "gate_no_stray_probe_files must run before gate_tests, same reason")
    assert body.count("run_gate(gate_no_stray_probe_files)") == 1, (
        "the gate must be wired into main() exactly once")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for t in tests:
        t()
        ok += 1
    print(f"OK: gate_no_stray_probe_files, {ok}/{len(tests)} checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
