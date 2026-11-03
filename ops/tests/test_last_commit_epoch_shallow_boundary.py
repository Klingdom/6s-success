#!/usr/bin/env python3
"""
Prove ops/preflight.py's _last_commit_epoch() refuses to trust a result
that lands on a shallow-clone boundary commit.

Found 2026-11-03, PM check-in: on a shallow clone, `git log -1 -- path`
does not error at the shallow boundary; it treats the boundary commit
(which has no visible parent locally) as having added every path in its
own tree, so a path untouched since well before the boundary reads back
with the boundary commit's own date. This cycle's gate_epub_edition_date_
current FAILed on exactly this shape: a boundary commit landed 2026-11-03,
content/book/'s real last commit is 2026-10-01, and the false 2026-11-03
reading looked newer than EDITION_DATE. Confirmed false by fully
unshallowing and re-running clean. This test builds a real git repo, makes
it shallow by hand the same way git itself would, and proves the function
now returns None (unmeasurable) instead of the boundary commit's date.

Run:  python ops/tests/test_last_commit_epoch_shallow_boundary.py
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _git(repo_dir, *args):
    subprocess.run(["git"] + list(args), cwd=repo_dir, check=True,
                    capture_output=True, text=True)


def _git_out(repo_dir, *args):
    return subprocess.run(["git"] + list(args), cwd=repo_dir, check=True,
                           capture_output=True, text=True).stdout.strip()


def _build_repo(tmp_dir):
    """touched.txt changes in commit 2 (the real last touch, old). Commit 3
    only changes other.txt, then gets grafted into looking like a shallow
    boundary with no visible parent, the same shape `git fetch --unshallow`
    leaves behind when it stops partway."""
    _git(tmp_dir, "init", "-q")
    _git(tmp_dir, "config", "user.email", "test@example.com")
    _git(tmp_dir, "config", "user.name", "Test")

    io.open(os.path.join(tmp_dir, "touched.txt"), "w").write("v1")
    io.open(os.path.join(tmp_dir, "other.txt"), "w").write("v1")
    _git(tmp_dir, "add", ".")
    _git(tmp_dir, "commit", "-q", "-m", "c1")

    io.open(os.path.join(tmp_dir, "touched.txt"), "w").write("v2, the real last touch")
    _git(tmp_dir, "add", ".")
    _git(tmp_dir, "commit", "-q", "-m", "c2 real last touch of touched.txt")

    io.open(os.path.join(tmp_dir, "other.txt"), "w").write("v2")
    _git(tmp_dir, "add", ".")
    _git(tmp_dir, "commit", "-q", "-m", "c3 only touches other.txt")
    boundary = _git_out(tmp_dir, "rev-parse", "HEAD")

    # Fake what a shallow clone's own boundary marker looks like: git
    # records the boundary commit's hash in .git/shallow. We leave full
    # history reachable (unlike a real shallow clone) so the test can also
    # assert the *correct* epoch once the boundary marker is removed.
    io.open(os.path.join(tmp_dir, ".git", "shallow"), "w").write(boundary + "\n")
    return boundary


def test_shallow_boundary_commit_returns_none_not_its_own_date():
    tmp_dir = tempfile.mkdtemp()
    try:
        _build_repo(tmp_dir)
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        try:
            # touched.txt's real last commit (c2) predates the boundary
            # (c3), so without the fix this would read back as c3's date.
            result = preflight._last_commit_epoch("touched.txt")
        finally:
            preflight.ROOT = real_root
        assert result is None, (
            "expected None (unmeasurable past a shallow boundary), got "
            "%r: the boundary commit's own date leaked through as if it "
            "were touched.txt's real last-touch date" % (result,))
        print("ok  a path last touched before the shallow boundary returns "
              "None, not the boundary commit's own date")
    finally:
        shutil.rmtree(tmp_dir)


def test_path_touched_by_the_boundary_commit_itself_also_returns_none():
    tmp_dir = tempfile.mkdtemp()
    try:
        _build_repo(tmp_dir)
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        try:
            # other.txt really was touched in the boundary commit itself,
            # but with no parent visible locally there is no way to tell
            # that apart from the false-positive shape, so this must still
            # read as unmeasurable rather than quietly assumed correct.
            result = preflight._last_commit_epoch("other.txt")
        finally:
            preflight.ROOT = real_root
        assert result is None, (
            "a shallow boundary commit's own date must never be trusted, "
            "even when it happens to be genuinely correct: got %r" % (result,))
        print("ok  a path genuinely touched by the boundary commit itself "
              "still returns None, since that can't be told apart locally")
    finally:
        shutil.rmtree(tmp_dir)


def test_without_the_shallow_marker_the_real_date_comes_back():
    tmp_dir = tempfile.mkdtemp()
    try:
        _build_repo(tmp_dir)
        os.remove(os.path.join(tmp_dir, ".git", "shallow"))
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        try:
            result = preflight._last_commit_epoch("touched.txt")
        finally:
            preflight.ROOT = real_root
        assert result is not None, "expected a real epoch once unshallowed"
        print("ok  with no shallow marker present, the real commit epoch "
              "is returned (proves the gate above isn't just always None)")
    finally:
        shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    test_shallow_boundary_commit_returns_none_not_its_own_date()
    test_path_touched_by_the_boundary_commit_itself_also_returns_none()
    test_without_the_shallow_marker_the_real_date_comes_back()
    print("\nall _last_commit_epoch shallow-boundary tests passed")
