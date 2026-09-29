"""Content-based worktree change detection, shared by gate self-tests.

git status --porcelain trusts the index stat cache and calls a file modified
the moment its mtime moves, even when a generator rewrote it with identical
bytes. preflight.worktree_changes() already documented and fixed this exact
trap for the real preflight run (a generator rewriting 189 pages moved 186
mtimes while git diff and git add -A both agreed nothing had changed). These
gate self-tests spin up their own throwaway git worktrees to prove a gate
fails on real drift and passes on a clean run; they need the same
content-based comparison, parameterized by that worktree's own path rather
than the real ROOT that preflight.worktree_changes() is hardcoded to.
"""
import subprocess


def changed_files(cwd: str) -> list:
    def names(*args) -> list:
        out = subprocess.run(["git"] + list(args), cwd=cwd,
                             capture_output=True, text=True).stdout
        return [x for x in out.splitlines() if x.strip()]

    return sorted(set(names("diff", "--name-only")
                      + names("diff", "--cached", "--name-only")
                      + names("ls-files", "--others", "--exclude-standard")))


def is_changed(cwd: str, path: str) -> bool:
    return path in changed_files(cwd)
