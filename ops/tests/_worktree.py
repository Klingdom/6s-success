"""Shared helper for tests that prove a gate leaves a git worktree clean.

Found 2026-09-29 in a scheduled preflight run: five test files
(test_gate_etsy_pdfs_current.py, test_gate_kdp_cover_current.py,
test_gate_kitchen_deck_current.py, test_gate_manual_print_fonts_current.py,
test_gate_prerender_shop_current.py) each do
`sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` then
`from _worktree import changed_files, is_changed`, but no ops/tests/_worktree.py
ever existed anywhere in this repository's git history. Every one of those
five files crashed at import time with ModuleNotFoundError the moment this
was checked directly rather than assumed clean because "tests" reported
green elsewhere.

The commit that added the five imports (09381b55f, "A shared root cause
told 100 pages to picture a surface 'at bedtime'") says in its own message
that it added this file ("New ops/tests/_worktree.py, and all [five tests]
switched to import it") and that it exists to replace `git status
--porcelain` with something immune to git's stat-cache trap
(`ops.preflight.worktree_changes()`'s own docstring: "git status --porcelain
calls a file modified as soon as its mtime moves... A generator that
rewrites a page with byte identical content moves the mtime every time").
The file was never actually staged in that commit, a plain `git add`
oversight. Reconstructed here from the commit's own description of what it
does, mirroring `worktree_changes()`'s content-comparison approach (`git
diff`, not `git status`) rather than reintroducing the exact trap the
commit message names, scoped to an arbitrary repo path rather than the
module-level ROOT `worktree_changes()` itself assumes.
"""
import subprocess


def changed_files(repo: str) -> list:
    """Every path with a real, content-level change in `repo`, tracked or
    not. `repo` is a real git working tree (its callers all run `git init`
    on a tempfile.mkdtemp() directory first).

    Uses `git diff` (content comparison) rather than `git status
    --porcelain` (which consults the index stat cache and calls a file
    modified as soon as its mtime moves, even when a generator rewrote it
    with byte-identical content), the same fix
    ops.preflight.worktree_changes() already made for the same reason.
    """
    def names(*args) -> list:
        out = subprocess.run(["git", "-C", repo] + list(args),
                            capture_output=True, text=True).stdout
        return [x for x in out.splitlines() if x.strip()]

    return sorted(set(names("diff", "--name-only")
                      + names("diff", "--cached", "--name-only")
                      + names("ls-files", "--others", "--exclude-standard")))


def is_changed(repo: str, path: str) -> bool:
    """Whether `path` (repo-relative) is among `repo`'s real changes."""
    return path in changed_files(repo)
