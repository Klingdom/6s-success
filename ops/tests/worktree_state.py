#!/usr/bin/env python3
"""Content-based worktree dirtiness for tests that run a generator.

WHY THIS EXISTS
---------------
`git status --porcelain` calls a file modified as soon as its mtime moves,
because what it consults first is the index stat cache. A generator that
rewrites a file with byte-identical content moves the mtime every time, so
status reports a change `git diff` cannot see.

ops/preflight.py's own worktree_changes() has said so since the day a gate
reported 186 files of "generator drift" on a tree where `git diff` was empty.
The tests exercising those same gates kept using status anyway, and on
2026-09-29 test_gate_kitchen_deck_current.py failed with:

    the gate left the worktree dirty on a clean run:
    ' M ops/cardtext/kitchen-deck.json'

on a file `cmp` proved byte-identical to HEAD. Whether it fails is a race:
git re-reads content only for entries it considers "racily clean", which is
what a fast fresh worktree usually produces and occasionally does not. So the
test was not wrong-today, it was flaky-always, and it failed in the direction
that costs most: red on a correct tree, which is how a suite stops being read.

Two directions matter, so both are provided:

  changed_files()  what really differs, for "a clean run left nothing behind"
  is_changed()     whether one path really differs, for "the gate left the
                   stale artifact modified rather than rewriting it"

The second exists because the stat cache lies the other way there: a test
asserting a file IS modified passes for free on any file the gate touched.
"""
import subprocess


def changed_files(cwd) -> list:
    """Every path differing from HEAD by CONTENT, plus untracked files."""
    def names(*args) -> list:
        out = subprocess.run(["git"] + list(args), cwd=cwd,
                             capture_output=True, text=True).stdout
        return [x for x in out.splitlines() if x.strip()]

    return sorted(set(names("diff", "--name-only")
                      + names("diff", "--cached", "--name-only")
                      + names("ls-files", "--others", "--exclude-standard")))


def is_changed(cwd, path) -> bool:
    """True when `path` really differs from HEAD, by content."""
    tail = path.replace("\\", "/").split("/")[-1]
    return any(p.replace("\\", "/").split("/")[-1] == tail
               for p in changed_files(cwd))
