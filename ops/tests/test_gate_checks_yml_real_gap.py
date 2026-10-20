#!/usr/bin/env python3
"""
Prove gate_checks_yml_real_gap can tell "checks.yml quiet because nothing
real changed" apart from "checks.yml quiet while real work shipped
unverified", and that it is wired into main() next to its sibling gate.

WHY THIS EXISTS
---------------
Found live 2026-10-20: checks.yml had not completed a run in 8+ hours, and a
PM check-in framed that as the workflow silently failing to trigger.
Verifying the actual commit list rather than the framing: every commit in
that window was either authored by `github-actions[bot]` pushing with the
default GITHUB_TOKEN (GitHub's own documented anti-recursion rule means such
a push can never trigger another workflow run, by design) or touched only
paths checks.yml already excludes. Nothing had actually shipped unverified;
the existing gate_ci_conclusion_current could not say so because it only
asks whether the last COMPLETED run was green, never whether a later real
commit exists with no run to show for it.

This test pins the distinction `_commits_touching_paths_since`'s new
`exclude_author` parameter and this gate make possible: a bot-only gap
passes clean, and a real commit with no later run FAILS, by name.

Run:  python ops/tests/test_gate_checks_yml_real_gap.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run(api_result, log_rows, trigger_paths=("ops/**",)):
    """Run the gate with the API and git log output both stubbed.

    log_rows is a list of (sha, author) tuples, newest first, exactly the
    shape `_commits_touching_paths_since` parses out of `git log
    --format=%H%x01%an`.
    """
    import dashboard
    old_api = preflight._workflow_run_via_api
    old_tok = dashboard.gh_token
    old_trigger = preflight._workflow_trigger_paths
    old_run = subprocess.run

    def fake_run(cmd, **kw):
        if cmd[:2] == ["git", "log"]:
            class R:
                returncode = 0
                stdout = "\n".join("%s\x01%s" % (sha, author)
                                    for sha, author in log_rows)
            return R()
        return old_run(cmd, **kw)

    preflight._workflow_run_via_api = lambda t, n: api_result
    dashboard.gh_token = lambda: "t"
    preflight._workflow_trigger_paths = lambda n: list(trigger_paths)
    preflight.subprocess.run = fake_run
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_checks_yml_real_gap()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight._workflow_run_via_api = old_api
        dashboard.gh_token = old_tok
        preflight._workflow_trigger_paths = old_trigger
        preflight.subprocess.run = old_run


def main():
    fails = []

    # 1. The real 2026-10-20 shape: every commit since the last completed
    #    run is bot-authored. Must pass clean, not flag a gap.
    f, w = _run(
        ("success", "2026-10-20T09:18:56Z", "3b61db7e2053", None),
        [("2334756", "github-actions"), ("3add4ef", "github-actions")],
    )
    if f:
        fails.append("a bot-only gap was flagged as a real gap: %r" % f)

    # 2. A real, non-bot commit with no later run: must FAIL, by name, and
    #    say how many.
    f, w = _run(
        ("success", "2026-10-20T09:18:56Z", "3b61db7e2053", None),
        [("2334756", "github-actions"), ("deadbee", "Claude")],
    )
    if not f:
        fails.append("a real non-bot gap was not flagged at all")
    elif f[0][0] != "checks-yml-real-gap" or "1 non-bot" not in f[0][1]:
        fails.append("the failure does not name the gate or the count: %r"
                      % (f[0][1][:120],))

    # 3. No commits at all since the last run: clean, the ordinary case.
    f, w = _run(
        ("success", "2026-10-20T09:18:56Z", "3b61db7e2053", None),
        [],
    )
    if f or w:
        fails.append("no commits since the last run was still flagged: %r %r"
                      % (f, w))

    # 4. gate_ci_conclusion_current already warns when the workflow cannot
    #    be queried at all; this sibling gate must stay silent rather than
    #    duplicate that warning.
    f, w = _run((None, None, None, "unknown"), [])
    if f or w:
        fails.append("an unqueryable workflow produced its own "
                      "finding here too (should defer to the sibling "
                      "gate): %r %r" % (f, w))

    # 5. Wired into main() immediately after its sibling, not just defined.
    import inspect
    src = inspect.getsource(preflight.main)
    before, _, after = src.partition("run_gate(gate_ci_conclusion_current)")
    if "run_gate(gate_checks_yml_real_gap)" not in after[:400]:
        fails.append("gate_checks_yml_real_gap is not wired into main() "
                      "right after gate_ci_conclusion_current")

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_checks_yml_real_gap, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
