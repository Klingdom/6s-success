#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_dashboard_self_description_fresh() catches a
real regression that recurred three times on 2026-10-02 (PM check-ins
20:4x, 21:4x, 22:2x): EXECUTIVE-DASHBOARD-LIVE.md's own "Last commit"
citation went stale after real commits landed, caught each time only by a
human comparing the file to `git log` by eye, with nothing in preflight to
catch it, the exact "lesson recorded in prose prevents nothing" shape
CLAUDE.md 10b warns against.

Builds small throwaway git repos (not this one) so the real-vs-own-output
commit classification can be proven deterministically, rather than hoping
this repository's own history happens to contain the right shape at test
time. dashboard.sh_checked()'s cwd default is reassigned to point at each
throwaway repo, since dashboard.ROOT is bound into that default at import
time and reassigning dashboard.ROOT alone would not move it.

Run:  python ops/tests/test_gate_dashboard_self_description_fresh.py
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import dashboard                                                 # noqa: E402


def _git(cwd, *args):
    subprocess.run(["git"] + list(args), cwd=cwd, check=True,
                    capture_output=True, text=True)


def _head(cwd):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd,
                           capture_output=True, text=True).stdout.strip()


def _commit(cwd, filename, content, message):
    with open(os.path.join(cwd, filename), "w", encoding="utf-8") as f:
        f.write(content)
    _git(cwd, "add", filename)
    _git(cwd, "commit", "-q", "-m", message)
    return _head(cwd)


def _new_repo(d):
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "test@example.com")
    _git(d, "config", "user.name", "Test")


def _write_dashboard(d, commit_hash, name="dash.md"):
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("| Field | Value |\n|---|---|\n"
                 "| Last commit | `%s` Some message |\n" % commit_hash[:9])
    return path


def _point_sh_checked_at(d):
    dashboard.sh_checked.__defaults__ = (d,)


def main() -> int:
    fails = []

    # 1. The pure function, in isolation.
    if dashboard.dashboard_citation_gap([]) is not None:
        fails.append("dashboard_citation_gap([]) must be None (nothing "
                      "real landed)")
    gap = dashboard.dashboard_citation_gap(["a" * 40])
    if gap is None or "1 real commit" not in gap:
        fails.append("dashboard_citation_gap() with one real commit "
                      "returned %r, expected it to name the count" % gap)

    orig_defaults = dashboard.sh_checked.__defaults__

    try:
        # 2a. Cited commit is the real current HEAD: no gap, no warning.
        with tempfile.TemporaryDirectory() as d:
            _new_repo(d)
            a = _commit(d, "real.txt", "v1", "real work A")
            _point_sh_checked_at(d)
            dash_fp = _write_dashboard(d, a)
            preflight.WARN.clear()
            preflight.gate_dashboard_self_description_fresh(dash_fp)
            if preflight.WARN:
                fails.append("citing the real current HEAD must not warn: "
                              "%r" % preflight.WARN)

        # 2b. Cited commit is one commit behind HEAD, and the one commit in
        #     between touches nothing but dashboard-own output: the
        #     unavoidable one-step lag dashboard.py cannot predict around.
        #     Must NOT warn.
        with tempfile.TemporaryDirectory() as d:
            _new_repo(d)
            a = _commit(d, "real.txt", "v1", "real work A")
            _commit(d, "EXECUTIVE-DASHBOARD-LIVE.md", "regen",
                    "dashboard regen only")
            _point_sh_checked_at(d)
            dash_fp = _write_dashboard(d, a)
            preflight.WARN.clear()
            preflight.gate_dashboard_self_description_fresh(dash_fp)
            if preflight.WARN:
                fails.append("a citation one dashboard-only commit behind "
                              "HEAD must not warn: %r" % preflight.WARN)

        # 2c. The real defect shape: the cited commit is behind HEAD, and a
        #     real (non-own-output) commit landed after the own-output
        #     regen commit with nobody rerunning dashboard.py. Must warn,
        #     naming exactly the one real commit, not the regen commit too.
        with tempfile.TemporaryDirectory() as d:
            _new_repo(d)
            a = _commit(d, "real.txt", "v1", "real work A")
            _commit(d, "EXECUTIVE-DASHBOARD-LIVE.md", "regen",
                    "dashboard regen only")
            _commit(d, "real.txt", "v2", "real work C, unreflected")
            _point_sh_checked_at(d)
            dash_fp = _write_dashboard(d, a)
            preflight.WARN.clear()
            preflight.gate_dashboard_self_description_fresh(dash_fp)
            if len(preflight.WARN) != 1:
                fails.append("a citation behind a real, unreflected commit "
                              "must warn exactly once: %r" % preflight.WARN)
            elif "1 real commit" not in preflight.WARN[0][1]:
                fails.append("warning did not name the real commit count "
                              "(the own-output regen commit must be "
                              "filtered out): %r" % (preflight.WARN[0],))

        # 2d. A citation that does not resolve at all (truncated hash that
        #     was never actually made, or a shallow clone): must warn about
        #     being unable to check, never claim freshness.
        with tempfile.TemporaryDirectory() as d:
            _new_repo(d)
            _commit(d, "real.txt", "v1", "real work A")
            _point_sh_checked_at(d)
            dash_fp = _write_dashboard(d, "0" * 40)
            preflight.WARN.clear()
            preflight.gate_dashboard_self_description_fresh(dash_fp)
            if not preflight.WARN:
                fails.append("an unresolvable cited commit must warn that "
                              "freshness could not be checked, not pass "
                              "silently")
    finally:
        dashboard.sh_checked.__defaults__ = orig_defaults

    # 3. No "Last commit" row at all: this should never happen to the real
    #    file (dashboard.py always writes it), so rather than silently pass
    #    this must warn that freshness could not be checked, the same
    #    CLAUDE.md 0.4 "unchecked is not passing" rule the gate follows for
    #    an unresolvable hash (2d above).
    with tempfile.TemporaryDirectory() as d2:
        no_row = os.path.join(d2, "none.md")
        with open(no_row, "w", encoding="utf-8") as f:
            f.write("# Nothing here\n")
        preflight.WARN.clear()
        preflight.gate_dashboard_self_description_fresh(no_row)
        if not preflight.WARN:
            fails.append("a file with no \"Last commit\" row must warn "
                          "that freshness could not be checked, not pass "
                          "silently")

    # 4. A missing file entirely: unmeasurable, must not warn.
    preflight.WARN.clear()
    preflight.gate_dashboard_self_description_fresh(
        "/nonexistent/path/does-not-exist.md")
    if preflight.WARN:
        fails.append("a missing file must not warn: %r" % preflight.WARN)

    # 5. The real, committed EXECUTIVE-DASHBOARD-LIVE.md must never FAIL
    #    (this is a warn-only gate; a crash or a FAIL would be a bug here).
    preflight.WARN.clear()
    preflight.FAIL.clear()
    preflight.gate_dashboard_self_description_fresh()
    if preflight.FAIL:
        fails.append("the real file must never FAIL (warn-only gate): %r"
                      % preflight.FAIL)

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 9/9 cases (fail-then-pass proved against synthetic repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
