#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_tracked_gitignored_dirs() fails when a file
git tracks sits inside a directory .gitignore says is generated, and stays
silent on a clean tree.

Found 2026-09-11 reading ops/render_cards.py cold, per CLAUDE.md step 5d: a
bare run globs build/card-fronts/*.html, a directory .gitignore lists as
generated. git ls-files showed 5 files tracked there anyway (a fossil of a
commit made before that gitignore line existed), so a cold run in a sandbox
with no other cards built saw only those 5 and reported two genuine
"overflows its box" failures that traced entirely to a hero photo the
sandbox does not have on disk, not to a real card defect. Confirmed directly
by planting a real placeholder PNG at the missing path and re-measuring the
same committed file clean. Fixed by `git rm --cached` on the 5 files; this
gate stops it recurring, for any of the 22 directories .gitignore names, not
only this one.

Run:  python ops/tests/test_gate_no_tracked_gitignored_dirs.py
"""
import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, capture_output=True,
                    check=True, text=True)


def _make_repo(tracked_in_ignored_dir: bool) -> str:
    tmp = tempfile.mkdtemp()
    _git(tmp, "init", "-q")
    _git(tmp, "config", "user.email", "test@example.com")
    _git(tmp, "config", "user.name", "test")
    io.open(os.path.join(tmp, ".gitignore"), "w", encoding="utf-8").write(
        "build/scratch/\n")
    os.makedirs(os.path.join(tmp, "build", "scratch"))
    kept = os.path.join(tmp, "kept.txt")
    io.open(kept, "w", encoding="utf-8").write("real content\n")
    _git(tmp, "add", "kept.txt", ".gitignore")
    if tracked_in_ignored_dir:
        stray = os.path.join(tmp, "build", "scratch", "old.html")
        io.open(stray, "w", encoding="utf-8").write("<html></html>")
        # add -f: this is exactly how the real fossil got in, a commit made
        # before (or overriding) the ignore rule.
        _git(tmp, "add", "-f", "build/scratch/old.html")
    _git(tmp, "commit", "-q", "-m", "init")
    return tmp


def _run(tracked_in_ignored_dir: bool):
    repo = _make_repo(tracked_in_ignored_dir)
    old_root = preflight.ROOT
    preflight.ROOT = repo
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_tracked_gitignored_dirs()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root


def test_clean_repo_passes():
    fails = _run(False)
    assert fails == [], f"expected no failure on a clean repo, got {fails}"


def test_tracked_file_in_ignored_dir_fails_by_name():
    fails = _run(True)
    assert len(fails) == 1 and fails[0][0] == "tracked-gitignored", fails
    assert "build/scratch/old.html" in fails[0][1], fails[0][1]


def test_registered_in_main_after_stray_probe_gate():
    src = io.open(os.path.join(ROOT, "ops", "preflight.py"),
                  encoding="utf-8").read()
    start = src.index("\ndef main(")
    body = src[start:]
    probe_pos = body.index("run_gate(gate_no_stray_probe_files)")
    this_pos = body.index("run_gate(gate_no_tracked_gitignored_dirs)")
    existing_pos = body.index("run_gate(gate_existing")
    assert probe_pos < this_pos < existing_pos, (
        "gate_no_tracked_gitignored_dirs should run early, beside "
        "gate_no_stray_probe_files, before gates that read site/ or build/ "
        "content can misread a fossil as something real")
    assert body.count("run_gate(gate_no_tracked_gitignored_dirs)") == 1


def test_real_repository_is_clean():
    """The actual fix: the 5 real fossils are untracked now, not just the
    synthetic case above."""
    old_root = preflight.ROOT
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_tracked_gitignored_dirs()
        assert preflight.FAIL == [], (
            f"the real repository should be clean after git rm --cached: "
            f"{preflight.FAIL}")
    finally:
        preflight.ROOT = old_root


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for t in tests:
        t()
        ok += 1
    print(f"OK: gate_no_tracked_gitignored_dirs, {ok}/{len(tests)} checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
